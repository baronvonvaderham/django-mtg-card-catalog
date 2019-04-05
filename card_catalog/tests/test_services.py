# -*- coding: utf-8 -*-
from django.test import TestCase

from card_catalog.services import ScryfallAPIService
from card_catalog.tests.api_test_data import *
from card_catalog.models import CardSet, Card, ScryfallCard

import vcr


class ScryfallAPIServiceTestCase(TestCase):
    """
    Tests for the Scryfall API Service
    """

    def setUp(self):
        self.real_card_set = CardSet.objects.create_set(TCG_EXPO_SET_DATA)
        self.real_card = Card.objects.create_card(tcg_card_data=TCG_EXPO_CARD_LIST[0],
                                                  card_set=self.real_card_set)
        self.test_set = CardSet.objects.create_set(TEST_SET_DATA)
        self.mishras_factory = Card.objects.create_card(tcg_card_data=MISHRAS_FACTORY_FALL_TCG_DATA,
                                                        card_set=self.test_set)
        self.plains = Card.objects.create_card(tcg_card_data=PLAINS_VARIANT_TCG_DATA,
                                               card_set=self.test_set)
        self.sdcc_gideon = Card.objects.create_card(tcg_card_data=SDCC_GIDEON_TCG_DATA,
                                                    card_set=self.test_set)

        self.service = ScryfallAPIService

        self.elves_scryfall_data = LLANOWAR_ELVES_SCRYFALL_DATA
        self.parsed_elves_data = {
            'color_identity': ['G'],
            'cmc': 1.0,
            'types': 'Creature — Elf Druid',
            'colors': ['G'],
            'name': 'Llanowar Elves',
            'mana_cost': '{G}',
            'oracle_text': '{T}: Add {G}.',
            'oracle_id': '68954295-54e3-4303-a6bc-fc4547a4e3a3'
        }

        self.flip_bolas_scryfall_data = FLIP_BOLAS_SCRYFALL_DATA
        self.parsed_flip_bolas_data = {
            'color_identity': ['B', 'R', 'U'],
            'mana_cost': ['{1}{U}{B}{R}', ''],
            'name': 'Nicol Bolas, the Ravager // Nicol Bolas, the Arisen',
            'oracle_text': [
                "Flying\nWhen Nicol Bolas, the Ravager enters the battlefield, each opponent discards a card.\n{4}{U}{B}{R}: Exile Nicol Bolas, the Ravager, then return him to the battlefield transformed under his owner's control. Activate this ability only any time you could cast a sorcery.",
                "+2: Draw two cards.\n−3: Nicol Bolas, the Arisen deals 10 damage to target creature or planeswalker.\n−4: Put target creature or planeswalker card from a graveyard onto the battlefield under your control.\n−12: Exile all but the bottom card of target player's library."],
            'colors': ['U', 'R', 'B'],
            'cmc': 4.0,
            'oracle_id': '55e4b27e-5447-4fc2-8cae-a03e344600c6',
            'types': 'Legendary Creature — Elder Dragon // Legendary Planeswalker — Bolas'
        }
        self.rumors_scryfall_data = RUMORS_SCRYFALL_DATA
        self.market_research_scryfall_data = MARKET_RESEARCH_SCRYFALL_DATA
        self.ultimate_nightmare_scryfall_data = ULTIMATE_NIGHTMARE_SCRYFALL_DATA
        self.bfm_left_scryfall_data = BFM_LEFT_SCRYFALL_DATA
        self.bfm_right_scryfall_data = BFM_RIGHT_SCRYFALL_DATA

    @vcr.use_cassette('vcr_cassettes/get_bulk_data_url.yaml')
    def test_get_bulk_data_url(self):
        url = self.service.get_bulk_data_url()
        self.assertTrue('scryfall-oracle-cards' in url)

    def test_retrieve_bulk_data(self):
        url = self.service.get_bulk_data_url()
        data = self.service.retrieve_bulk_data(url)
        self.assertIsInstance(data, list)

    def test_parse_card_info(self):
        # Start with a simple card, Llanowar Elves
        parsed_data = self.service.parse_card_info(self.elves_scryfall_data)
        for key, value in self.parsed_elves_data.items():
            self.assertEquals(value, parsed_data.get(key))

        # Now we need to test a split/flip card to trigger that if branch
        parsed_data = self.service.parse_card_info(self.flip_bolas_scryfall_data)
        for key, value in self.parsed_flip_bolas_data.items():
            if isinstance(value, list):
                self.assertEquals(sorted(value), sorted(parsed_data.get(key)))
            else:
                self.assertEquals(value, parsed_data.get(key))

    def test_create_local_scryfall_card(self):
        # Test creating normal card
        elves = self.service.create_local_scryfall_card(self.elves_scryfall_data)
        self.assertTrue(elves[0])
        self.assertIsInstance(elves[1], ScryfallCard)

        # Test flip card
        bolas = self.service.create_local_scryfall_card(self.flip_bolas_scryfall_data)
        self.assertTrue(bolas[0])
        self.assertIsInstance(bolas[1], ScryfallCard)

        # Test each exception that had to be hard-coded for
        rumors = self.service.create_local_scryfall_card(self.rumors_scryfall_data)
        self.assertTrue(rumors[0])
        self.assertIsInstance(rumors[1], ScryfallCard)

        market_research = self.service.create_local_scryfall_card(self.market_research_scryfall_data)
        self.assertTrue(market_research[0])
        self.assertIsInstance(market_research[1], ScryfallCard)

        nightmare = self.service.create_local_scryfall_card(self.ultimate_nightmare_scryfall_data)
        self.assertTrue(nightmare[0])
        self.assertIsInstance(nightmare[1], ScryfallCard)

        bfm_left = self.service.create_local_scryfall_card(self.bfm_left_scryfall_data)
        self.assertTrue(bfm_left[0])
        self.assertIsInstance(bfm_left[1], ScryfallCard)

        bfm_right = self.service.create_local_scryfall_card(self.bfm_right_scryfall_data)
        self.assertTrue(bfm_right[0])
        self.assertIsInstance(bfm_right[1], ScryfallCard)

    def test_update_card_from_scryfall(self):
        # Test with real card, Arid Mesa
        arid_mesa_scryfall = self.service.create_local_scryfall_card(ARID_MESA_SCRYFALL_DATA)
        self.assertTrue(arid_mesa_scryfall[0])
        updated_mesa = self.service.update_card_from_scryfall(card=self.real_card)
        self.assertEquals(updated_mesa.cmc, 0)
        self.assertEquals(updated_mesa.oracle_text, MESA_ORACLE_TEXT)

        # Test with Basic Land variant that has parentheses
        plains_scryfall = self.service.create_local_scryfall_card(PLAINS_SCRYFALL_DATA)
        self.assertTrue(plains_scryfall[0])
        updated_plains = self.service.update_card_from_scryfall(card=self.plains)
        self.assertEquals(updated_plains.cmc, 0)
        self.assertEquals(updated_plains.oracle_text, '({T}: Add {W}.)')

        # Test with art variant card with parentheses - Mishra's Factory (Fall)
        factory_scryfall = self.service.create_local_scryfall_card(MISHRAS_FACTORY_SCRYFALL_DATA)
        self.assertTrue(factory_scryfall[0])
        updated_factory = self.service.update_card_from_scryfall(card=self.mishras_factory)
        self.assertEquals(updated_factory.cmc, 0)
        self.assertEquals(updated_factory.oracle_text, FACTORY_ORACLE_TEXT)

        # Test with an SDCC Exclusive Planeswalker
        gideon_scryfall = self.service.create_local_scryfall_card(GIDEON_SCRYFALL_DATA)
        self.assertTrue(gideon_scryfall[0])
        updated_gideon = self.service.update_card_from_scryfall(card=self.sdcc_gideon)
        self.assertEquals(updated_gideon.mana_cost, '{2}{W}{W}')
        self.assertEquals(updated_gideon.cmc, 4)
        self.assertEquals(updated_gideon.oracle_text, GIDEON_ORACLE_TEXT)
        self.assertEquals(updated_gideon.types, "['Legendary', 'Planeswalker']")
        self.assertEquals(updated_gideon.subtypes, "['Gideon']")
