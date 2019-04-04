# -*- coding: utf-8 -*-
from django.db import transaction

from celery.schedules import crontab
from celery.task import PeriodicTask, group
from celery.utils.log import get_task_logger

from .constants import EXCLUDED_CARD_NAMES, EXCLUDED_SETS
from .models import CardSet, Card, ScryfallCard, CardPrice
from .services import CardCatalogSyncService, ScryfallAPIService
from celery_app import app

logger = get_task_logger('tasks.common')


class ScryfallSyncTask(PeriodicTask):
    name = 'scryfall-sync-task'
    run_every = crontab(hour=3)

    def run(self, *args, **kwargs):
        logger.info('BEGINNING SCRYFALL SYNC TASK')
        bulk_data_url = ScryfallAPIService.get_bulk_data_url()
        scryfall_data = ScryfallAPIService.retrieve_bulk_data(bulk_data_url)
        load_tasks = []
        for card in scryfall_data:
            card_check = ScryfallCard.objects.filter(oracle_id=card.get('oracle_id')).first()
            if not card_check:
                load_tasks.append(get_or_create_scryfall_card.s(card))
        task_group = group(load_tasks)
        group_complete = task_group.apply()


@app.task(name='get_or_create_scryfall_card')
def get_or_create_scryfall_card(card_data):
    created, card = ScryfallAPIService.create_local_scryfall_card(card_data)
    if created:
        logger.info('Created new Scryfall card: {}'.format(card.name))


class SetSyncTask(PeriodicTask):
    name = 'set-sync-task'
    run_every = crontab(hour=3, minute=15)

    def run(self, *args, **kwargs):
        with transaction.atomic():
            logger.info('BEGINNING SET SYNC TASK')
            tcg_service = CardCatalogSyncService()
            set_list = tcg_service.list_all_sets()
            counter = 0
            for each_set in set_list:
                if each_set.get('name') in EXCLUDED_SETS:
                    continue
                try:
                    card_set = CardSet.objects.get(name=each_set.get('name'))
                except CardSet.DoesNotExist:
                    card_set = None
                if (not card_set) and (not each_set.get('name') == 'World Championship Decks'):
                    new_set = create_new_set(each_set)
                    logger.info('CREATED NEW SET: {}'.format(new_set))
                    counter += 1


class CardSyncTask(PeriodicTask):
    name = 'card-sync-task'
    run_every = crontab(hour=4)

    def run(self, *args, **kwargs):
        with transaction.atomic():
            tcg_service = CardCatalogSyncService()
            set_list = CardSet.objects.all()
            load_tasks = []
            for each_set in set_list:
                card_list = each_set.get_cards_for_set()
                tcg_data = tcg_service.retrieve_product_list_for_set(each_set.tcgplayer_group_id)
                if not card_list:
                    logger.info("Spawning task to create cards for {}".format(each_set))
                    # If we have no cards at all for this set, it's a new set, make all new cards
                    load_tasks.append(create_all_new_cards.s(card_set_id=each_set.id, tcg_data=tcg_data))
                elif len(card_list) != len(tcg_data):
                    logger.info("Checking cards in {}".format(each_set))
                    # If the length of these sets doesn't match, likely a new card was added to
                    # the set since last sync (mostly applicable to promo sets)
                    for tcg_card in tcg_data:
                        # Filter to see if the card exists in the current set card list
                        card = card_list.filter(tcg_product_id=tcg_card.get('productId'))
                        if not card:
                            create = True
                            for exclusion in EXCLUDED_CARD_NAMES:
                                if exclusion in tcg_card.get('name'):
                                    create = False
                            if tcg_card.get('name').endswith('Deck') or not create:
                                continue
                            # Card doesn't exist, so create it
                            load_tasks.append(create_new_card.s(card_set_id=each_set.id, tcg_data=tcg_card))
            task_group = group(load_tasks)
            group_complete = task_group.apply()
            logger.info('CARD SYNC TASK COMPLETE!')


class PriceSyncTask(PeriodicTask):
    name = 'price-sync-task'
    run_every = crontab(hour=5)

    def run(self, *args, **kwargs):
        with transaction.atomic():
            tcg_service = CardCatalogSyncService()
            set_list = CardSet.objects.all()
            load_tasks = []
            for each_set in set_list:
                logger.info("Syncing prices for {}".format(each_set))
                tcg_data = tcg_service.get_prices_for_set(set_id=each_set.id)
                load_tasks.append(log_set_pricing.s(card_set=each_set, tcg_data=tcg_data))
            task_group = group(load_tasks)
            group_complete = task_group.apply_async()
            logger.info('CARD SYNC TASK COMPLETE!')


def create_new_set(new_set):
    return CardSet.objects.create_set(new_set)


@app.task(name='create-all-new-cards-for-set')
def create_all_new_cards(card_set_id, tcg_data):
    cards_created = 0
    card_set = CardSet.objects.get(id=card_set_id)
    for card in tcg_data:
        create = True
        for exclusion in EXCLUDED_CARD_NAMES:
            if exclusion in card.get('name'):
                create = False
        if create and not card.get('name').endswith('Deck'):
            # logger.info(card.get('name'))
            Card.objects.create_card(tcg_card_data=card, card_set=card_set)
            cards_created += 1
    logger.info('{} new cards created for set {}'.format(cards_created, card_set))


@app.task(name='create-single-new-card')
def create_new_card(card_set_id, tcg_data):
    card_set = CardSet.objects.get(id=card_set_id)
    new_card = Card.objects.create_card(tcg_card_data=tcg_data, card_set=card_set)
    logger.info('Added card {} to existing set {}'.format(new_card.name, card_set))


@app.task(name='log-set-pricing')
def log_set_pricing(card_set, tcg_data):
    cards = 0
    for item in tcg_data:
        success, _ = CardPrice.objects.update_or_create(item)
        if success:
            cards += 1
    logger.info('Logged pricing for {} cards in set {}'.format(cards, card_set))
