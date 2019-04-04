# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
import datetime
import card_catalog.settings as settings
import unicodedata

from card_catalog.services import ScryfallAPIService


class CardSetManager(models.Manager):

    def create_set(self, tcg_set_data):
        code = tcg_set_data.get('abbreviation')
        name = tcg_set_data.get('name')
        tcgplayer_group_id = tcg_set_data.get('groupId')
        release_date, time = tcg_set_data.get('publishedOn').split('T')
        release_date = release_date
        card_set = self.create(
            code=code,
            name=name,
            tcgplayer_group_id=tcgplayer_group_id,
            release_date=release_date
        )
        card_set.save()
        return card_set


class CardSet(models.Model):
    """
    Class to contain the card sets to be referenced by the Card model
    """
    code = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    tcgplayer_group_id = models.IntegerField(blank=False, null=False)
    release_date = models.DateField(blank=False, null=False)

    objects = CardSetManager()

    def __str__(self):
        return '{} [{}]'.format(self.name, self.code)

    def get_cards_for_set(self):
        return Card.objects.filter(set__name=self.name)


class CardManager(models.Manager):

    def create_card(self, tcg_card_data, card_set):
        name = tcg_card_data.get('name')
        tcg_product_id = tcg_card_data.get('productId')
        product_url = tcg_card_data.get('url')
        image_url = tcg_card_data.get('imageUrl')
        card = self.create(
            name=name,
            tcg_product_id=tcg_product_id,
            product_url=product_url,
            image_url=image_url,
            set=card_set
        )
        card = ScryfallAPIService.update_card_from_scryfall(card)
        card.save()
        return card


class Card(models.Model):
    """
    Class to contain the existing cards to be referenced by a cube list
    """
    name = models.CharField(max_length=256)
    tcg_product_id = models.CharField(max_length=64)
    set = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    product_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    mana_cost = models.CharField(max_length=128, blank=True, null=True)
    cmc = models.IntegerField(blank=True, null=True)
    types = models.CharField(max_length=256, blank=True, null=True)
    subtypes = models.CharField(max_length=256, blank=True, null=True)
    colors = models.CharField(max_length=128, blank=True, null=True)
    color_identity = models.CharField(max_length=128, blank=True, null=True)
    oracle_text = models.CharField(max_length=2048, blank=True, null=True)

    objects = CardManager()

    def __str__(self):
        return "{} [{}]".format(self.name, self.set.code)

    @property
    def affiliate_link(self):
        return self.product_url + '&partner={}'.format(settings.TCG_AFFILIATE_PARTNER_CODE)


class ScryfallCardManager(models.Manager):

    def get_or_create_card(self, data):
        card = self.filter(oracle_id=data.get('oracle_id')).first()
        if not card:
            return True, self.create_card(data)
        else:
            return False, card

    def create_card(self, data):
        types = data.get('types')
        card_types = []
        card_subtypes = []
        if types:
            # Need to account for split cards that have complex type lines...stupid Kamigawa
            if ' // ' in types:
                first_type_line, second_type_line = types.split(' // ')
            else:
                first_type_line = types
                second_type_line = None
            # If there is a ' - ', that means we have subtypes to the right, supertypes to the left
            for type_line in (first_type_line, second_type_line):
                if not type_line:
                    continue
                if ' — ' in type_line:
                    types, subtypes = type_line.split(' — ')
                else:
                    types = type_line
                    subtypes = None
                if subtypes:
                    if ' ' in subtypes:
                        for subtype in subtypes.split(' '):
                            card_subtypes.append(subtype)
                    else:
                        card_subtypes.append(subtypes)
                if ' ' in types:
                    for card_type in types.split(' '):
                        card_types.append(card_type)
                else:
                    card_types.append(types)
        card = self.create(
            oracle_id=data.get('oracle_id'),
            name=''.join(c for c in unicodedata.normalize('NFD', data.get('name')) if unicodedata.category(c) != 'Mn'),
            mana_cost=data.get('mana_cost'),
            cmc=data.get('cmc'),
            types=card_types,
            subtypes=card_subtypes,
            colors=data.get('colors'),
            color_identity=data.get('color_identity'),
            oracle_text=data.get('oracle_text'),
        )
        return card


class ScryfallCard(models.Model):
    """
    Class to contain a local version of the scryfall data to limit the need for external API calls

    NOTE: Only intended for use as a proxy for the scryfall API for updating the Card models without having
    to make tens of thousands of calls to the external API endpoint.
    """
    oracle_id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    mana_cost = models.CharField(max_length=128, blank=True, null=True)
    cmc = models.IntegerField(blank=True, null=True)
    types = models.CharField(max_length=256, blank=True, null=True)
    subtypes = models.CharField(max_length=256, blank=True, null=True)
    colors = models.CharField(max_length=128, blank=True, null=True)
    color_identity = models.CharField(max_length=128, blank=True, null=True)
    oracle_text = models.CharField(max_length=2048, blank=True, null=True)

    objects = ScryfallCardManager()


class CardPriceManager(models.Manager):

    def update_or_create_price(self, data):
        price_entry = self.filter(card__tcg_product_id=data.get('productId'), date=datetime.date.today())
        if price_entry:
            return False, self.update_price(price_entry, data)
        else:
            return True, self.create_price(data)

    def create_price(self, data):
        card = Card.objects.get(tcg_product_id=data.get('productId'))
        if data.get('subTypeName') == 'Normal':
            price_entry = self.create(
                card=card,
                low=data.get('lowPrice'),
                mid=data.get('midPrice'),
                high=data.get('highPrice'),
                market=data.get('marketPrice'),
            )
        elif data.get('subtypeName') == 'Foil':
            price_entry = self.create(
                card=card,
                foil_low=data.get('lowPrice'),
                foil_mid=data.get('midPrice'),
                foil_high=data.get('highPrice'),
                foil_market=data.get('marketPrice'),
            )
        return price_entry

    def update_price(self, price_entry, data):
        if data.get('subTypeName') == 'Normal':
            price_entry.low = data.get('lowPrice')
            price_entry.mid = data.get('midPrice')
            price_entry.high = data.get('highPrice')
            price_entry.market = data.get('marketPrice')
        elif data.get('subTypeName') == 'Foil':
            price_entry.foil_low = data.get('lowPrice')
            price_entry.foil_mid = data.get('midPrice')
            price_entry.foil_high = data.get('highPrice')
            price_entry.foil_market = data.get('marketPrice')
        price_entry.save()
        return price_entry


class CardPrice(models.Model):
    """
    Class to contain timestamped pricing data from TCGPlayer, synced daily.
    """
    card = models.ForeignKey(Card, blank=False, null=False, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, blank=False, null=False)
    low = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    mid = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    high = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    market = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    foil_low = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    foil_mid = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    foil_high = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)
    foil_market = models.DecimalField(blank=True, null=True, max_digits=20, decimal_places=2)

    objects = CardPriceManager()
