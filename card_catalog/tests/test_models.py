# -*- coding: utf-8 -*-
from django.test import TestCase
from card_catalog.settings import TCG_AFFILIATE_PARTNER_CODE

from card_catalog.tests.api_test_data import (
    TCG_EXPO_SET_DATA,
    TCG_EXPO_CARD_LIST,
    TENTH_EDITION_SET_DATA,
    LLANOWAR_ELVES_SCRYFALL_DATA,
)
from card_catalog.models import Card, CardSet, ScryfallCard


class CardSetAndCardTestCase(TestCase):
    """
    Tests for the card_catalog models
    """

    def setUp(self):
        self.exp_set_data = TCG_EXPO_SET_DATA
        self.exp_cards_data = TCG_EXPO_CARD_LIST
        self.tenth_ed_set_data = TENTH_EDITION_SET_DATA

    def test_models(self):
        card_set = CardSet.objects.create_set(tcg_set_data=self.exp_set_data)
        self.assertTrue(isinstance(card_set, CardSet))
        self.assertEquals(card_set.release_date, '2015-10-02')
        self.assertEqual(card_set.__str__(), 'Zendikar Expeditions [EXP]')

        card = Card.objects.create_card(
            tcg_card_data=self.exp_cards_data[1],
            card_set=card_set
        )
        self.assertTrue(isinstance(card, Card))
        self.assertEquals(card.tcg_product_id, 104307)
        self.assertEquals(card.__str__(), "Steam Vents [EXP]")
        self.assertEquals(
            card.affiliate_link,
            "https://store.tcgplayer.com/magic/zendikar-expeditions/steam-vents&partner={}".format(
                TCG_AFFILIATE_PARTNER_CODE)
        )

        second_set = CardSet.objects.create_set(tcg_set_data=self.tenth_ed_set_data)
        second_card = Card.objects.create_card(
            tcg_card_data=self.exp_cards_data[0],
            card_set=second_set
        )
        all_cards = Card.objects.all()
        self.assertEquals(len(all_cards), 2)
        first_set_cards = Card.objects.filter(set=card_set)
        self.assertEqual(len(card_set.get_cards_for_set()), 1)

        scryfall_card = ScryfallCard.objects.get_or_create_card(LLANOWAR_ELVES_SCRYFALL_DATA)
        self.assertTrue(scryfall_card[0])
        self.assertIsInstance(scryfall_card[1], ScryfallCard)
        # If we make the same call, it sould still return the card, but also return False
        # to indicate that the new card was not created
        scryfall_card_duplicate = ScryfallCard.objects.get_or_create_card(LLANOWAR_ELVES_SCRYFALL_DATA)
        self.assertFalse(scryfall_card_duplicate[0])
        self.assertIsInstance(scryfall_card_duplicate[1], ScryfallCard)
