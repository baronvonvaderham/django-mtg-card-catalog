# -*- coding: utf-8 -*-
from django.test import TestCase

from card_catalog.models import CardSet, Card, ScryfallCard
from card_catalog.services import ScryfallAPIService
from card_catalog.tasks import SetSyncTask, CardSyncTask, ScryfallSyncTask
from .api_test_data import TCG_EXPO_SET_DATA, MEDIA_PROMOS_SET_DATA, CURATOR_TCG_DATA, SEVENTH_EDITION_SET_DATA

import vcr


class ScryfallSyncTasksTestCase(TestCase):

    def test_scryfall_sync(self):
        scryfall_sync_task = ScryfallSyncTask().s(test=True).apply()
        self.assertEquals(scryfall_sync_task.state, 'SUCCESS')
        scryfall_cards = ScryfallCard.objects.all()
        # Just test that we created a model per item in the scryfall data
        self.assertEquals(len(scryfall_cards), 2)


class TCGSyncTasksTestCase(TestCase):

    @vcr.use_cassette('vcr_cassettes/set_sync.yml')
    def test_set_sync(self):
        set_sync_task = SetSyncTask().s(test=True).apply()
        self.assertEquals(set_sync_task.state, 'SUCCESS')
        set_list = CardSet.objects.all()
        # As of creation on 10/27/18, there are 227 sets available, that can only go up
        self.assertEquals(len(set_list), 2)

    @vcr.use_cassette('vcr_cassettes/card_sync.yml')
    def test_card_sync(self):
        # Only testing for a single set so we don't have to wait forever
        card_set = CardSet.objects.create_set(tcg_set_data=TCG_EXPO_SET_DATA)
        # Just confirm there is only one set present just to be sure
        self.assertEquals(len(CardSet.objects.all()), 1)
        card_sync_task = CardSyncTask().s(test=True).apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        card_list = Card.objects.all()
        # There are a total of 45 Zendikar Expeditions, this will not change
        self.assertEquals(len(card_list), 2)

        # Now delete a card and re-run. It should re-sync just the missing card
        Card.objects.get(name='Steam Vents').delete()
        card_list = Card.objects.all()
        # Now this query should return 44
        self.assertEquals(len(card_list), 1)
        # Re-run the sync task now
        card_sync_task = CardSyncTask().s(test=True).apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        card_list = Card.objects.all()
        # We should be back up to 45 cards in the set
        self.assertEquals(len(card_list), 2)

        # Need to test exclusions, so need to do another set for that
        card_set.delete()
        self.assertEquals(len(CardSet.objects.all()), 0)
        card_set = CardSet.objects.create_set(tcg_set_data=MEDIA_PROMOS_SET_DATA)
        self.assertEquals(len(CardSet.objects.all()), 1)
        card_sync_task = CardSyncTask().s().apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        test_card = Card.objects.filter(name__icontains='Planeswalkers Set')
        self.assertEquals(len(test_card), 0)

        card_list = Card.objects.all()
        card_list.delete()
        card_list = Card.objects.all()
        self.assertEquals(len(card_list), 0)
        curator = Card.objects.create_card(tcg_card_data=CURATOR_TCG_DATA, card_set=card_set)
        card_list = card_set.get_cards_for_set()
        self.assertEquals(len(card_list), 1)
        card_sync_task = CardSyncTask().s().apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        test_card = Card.objects.filter(name__icontains='Planeswalkers Set')
        self.assertEquals(len(test_card), 0)

    @vcr.use_cassette('vcr_cassettes/all_product_sync.yaml')
    def test_all_products_sync(self):
        # Test that using 'sync_all_products' argument allows things like theme decks and boosters
        self.assertEquals(len(CardSet.objects.all()), 0)
        card_set = CardSet.objects.create_set(tcg_set_data=SEVENTH_EDITION_SET_DATA)
        self.assertEquals(len(CardSet.objects.all()), 1)
        card_sync_task = CardSyncTask().s(sync_all_products=True).apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        theme_decks = Card.objects.filter(name__icontains='Deck')
        # 7th Edition had 5 theme decks total
        self.assertEqual(len(theme_decks), 5)
        boosters = Card.objects.filter(name__icontains='Booster')
        # Should be 2, Booster Pack and Booster Box
        self.assertEqual(len(boosters), 2)
