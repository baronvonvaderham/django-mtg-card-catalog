# -*- coding: utf-8 -*-
from django.test import TestCase

from card_catalog.models import CardSet, Card, ScryfallCard
from card_catalog.services import ScryfallAPIService
from card_catalog.tasks import SetSyncTask, CardSyncTask, ScryfallSyncTask
from .api_test_data import TCG_EXPO_SET_DATA, MEDIA_PROMOS_SET_DATA, CURATOR_TCG_DATA


class ScryfallSyncTasksTestCase(TestCase):

    def test_scryfall_sync(self):
        scryfall_sync_task = ScryfallSyncTask().s().apply()
        self.assertEquals(scryfall_sync_task.state, 'SUCCESS')
        scryfall_cards = ScryfallCard.objects.all()
        scryfall_service = ScryfallAPIService()
        scryfall_url = scryfall_service.get_bulk_data_url()
        scryfall_data = scryfall_service.retrieve_bulk_data(scryfall_url)
        # Just test that we created a model per item in the scryfall data
        self.assertEquals(len(scryfall_cards), len(scryfall_data))


class TCGSyncTasksTestCase(TestCase):

    def test_set_sync(self):
        set_sync_task = SetSyncTask().s().apply()
        self.assertEquals(set_sync_task.state, 'SUCCESS')
        set_list = CardSet.objects.all()
        # As of creation on 10/27/18, there are 227 sets available, that can only go up
        self.assertGreaterEqual(len(set_list), 220)

    def test_card_sync(self):
        # Only testing for a single set so we don't have to wait forever
        card_set = CardSet.objects.create_set(tcg_set_data=TCG_EXPO_SET_DATA)
        # Just confirm there is only one set present just to be sure
        self.assertEquals(len(CardSet.objects.all()), 1)
        card_sync_task = CardSyncTask().s().apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        card_list = Card.objects.all()
        # There are a total of 45 Zendikar Expeditions, this will not change
        self.assertEquals(len(card_list), 45)

        # Now delete a card and re-run. It should re-sync just the missing card
        Card.objects.get(name='Steam Vents').delete()
        card_list = Card.objects.all()
        # Now this query should return 44
        self.assertEquals(len(card_list), 44)
        # Re-run the sync task now
        card_sync_task = CardSyncTask().s().apply()
        self.assertEquals(card_sync_task.state, 'SUCCESS')
        card_list = Card.objects.all()
        # We should be back up to 45 cards in the set
        self.assertEquals(len(card_list), 45)

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
