# -*- coding: utf-8 -*-
import requests
import json
import time
import unicodedata
from celery.utils.log import get_task_logger

from card_catalog.constants import (
    TCG_BEARER_TOKEN_URL,
    TCG_ALL_SETS_URL,
    TCG_CARD_LIST_FOR_SET_URL,
    TCG_PRICES_FOR_SET_URL,
    BASIC_TYPES,
)
from card_catalog.settings import TCG_API_PRIVATE_KEY, TCG_API_PUBLIC_KEY

logger = get_task_logger('tasks.common')


class CardCatalogSyncService(object):

    def __init__(self):
        self.bearer_token = self.get_bearer_token()

    @staticmethod
    def get_bearer_token():
        url = TCG_BEARER_TOKEN_URL
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = 'grant_type=client_credentials&client_id={public_key}&client_secret={private_key}'.format(
            public_key=TCG_API_PUBLIC_KEY,
            private_key=TCG_API_PRIVATE_KEY
        )
        response = requests.post(url, headers=headers, data=data)
        return json.loads(response.text).get('access_token')

    def execute_chunked_query(self, url, category_id=1, set_group_id=None):
        headers = {
            'Accept': 'application/json',
            'Authorization': 'bearer {}'.format(self.bearer_token),
        }
        params = {
            'categoryId': category_id,
            'limit': 100
        }
        if set_group_id:
            params['groupId'] = set_group_id
        response = requests.request('GET', url, headers=headers, params=params)
        total_items = json.loads(response._content.decode('utf8')).get('totalItems')
        if not total_items:
            return json.loads(response._content.decode('utf8')).get('results')
        queries_required = int(int(total_items) / 100) + 1 if total_items else 0
        results = []
        if queries_required:
            for x in range(0, queries_required):
                params['offset'] = x * 100
                results += self.get_chunk(url, headers, params)
        return results

    @staticmethod
    def get_chunk(url, headers, params):
        return json.loads(requests.request('GET', url, headers=headers, params=params).text).get('results')

    def list_all_sets(self):
        url = TCG_ALL_SETS_URL
        return self.execute_chunked_query(url=url)

    def retrieve_product_list_for_set(self, set_group_id):
        url = TCG_CARD_LIST_FOR_SET_URL
        return self.execute_chunked_query(url=url, set_group_id=set_group_id)

    def get_prices_for_set(self, set_id):
        url = TCG_PRICES_FOR_SET_URL.format(set_id)
        return self.execute_chunked_query(url=url, set_group_id=set_id)


class ScryfallAPIService:

    @staticmethod
    def parse_card_info(data):
        # Need to handle how Scryfall returns split/flip cards, with two card face objects embedded in the response
        if "//" in data.get('name'):
            mana_cost = []
            colors = []
            oracle_text = []
            for card_face in data.get('card_faces'):
                mana_cost.append(card_face.get('mana_cost'))
                if card_face.get('colors'):
                    for color in card_face.get('colors'):
                        colors.append(color)
                oracle_text.append(card_face.get('oracle_text'))
            colors = list(set(colors))
        else:
            mana_cost = data.get('mana_cost')
            colors = data.get('colors')
            oracle_text = data.get('oracle_text')
        return {
            'oracle_id': data.get('oracle_id'),
            'name': data.get('name'),
            'mana_cost': mana_cost,
            'cmc': int(data.get('cmc')),
            'types': data.get('type_line'),
            'colors': colors,
            'color_identity': data.get('color_identity'),
            'oracle_text': oracle_text,
        }

    @staticmethod
    def update_card_from_scryfall(card):
        from card_catalog.models import ScryfallCard
        card_name = ''.join(c for c in unicodedata.normalize('NFD', card.name) if unicodedata.category(c) != 'Mn')
        scryfall_data = ScryfallCard.objects.filter(name=card_name).last()
        if not scryfall_data:
            if card.name.split(' ')[0] in BASIC_TYPES:
                # Handle the plethora of bizarre basic lands
                scryfall_data = ScryfallCard.objects.filter(name=card.name.split(' ')[0]).last()
            elif '(Showcase)' in card.name:
                # Handle Showcase Cards
                new_name = card.name[:-11]
                scryfall_data = ScryfallCard.objects.filter(name__icontains=new_name).last()
            elif "(" in card.name or "[" in card.name:
                # If card name contains ( or [, then it has a parenthetical/bracketed variants to ignore
                split_terms = card.name.split(' ')
                new_name = ''
                for term in split_terms:
                    # Check if the term is the first one that has the parentheses/brackets
                    if '(' in term or '[' in term:
                        # If so, chop off the trailing space and stop looping
                        new_name = new_name[:-1]
                        break
                    # Otherwise, tack the term onto the end of the new name string with a space
                    new_name += term + ' '
                scryfall_data = ScryfallCard.objects.filter(name=new_name).last()
            elif 'EXCLUSIVE' in card.name:
                # Handle Messy SDCC Exclusives
                if card.name.endswith('EXCLUSIVE'):
                    new_name = card.name[:-20]
                else:
                    new_name = card.name[:20]
                scryfall_data = ScryfallCard.objects.filter(name__icontains=new_name).last()
            else:
                scryfall_data = ScryfallCard.objects.filter(name__icontains=card.name).last()
        try:
            card.mana_cost = scryfall_data.mana_cost
            card.cmc = scryfall_data.cmc
            card.colors = scryfall_data.colors
            card.color_identity = scryfall_data.color_identity
            card.oracle_text = scryfall_data.oracle_text
            card.types = scryfall_data.types
            card.subtypes = scryfall_data.subtypes
        except AttributeError:
            logger.error("COULD NOT UPDATE CARD: {}".format(card))
            logger.error(card.__dict__)
        card.save()
        return card

    @staticmethod
    def create_local_scryfall_card(card):
        from card_catalog.models import ScryfallCard

        parsed_data = ScryfallAPIService.parse_card_info(card)
        # Need to add some one-off exceptions due to stupid differences
        if 'Rumors of My Death' in parsed_data.get('name'):
            # Dumb extra spaces inside of the ellipsis
            parsed_data['name'] = '"Rumors of My Death..."'
        if (parsed_data.get('name') == 'Our Market Research Shows That Players Like Really Long Card Names So We Made '
                                       'this Card to Have the Absolute Longest Card Name Ever Elemental'):
            # TCGPlayer truncates this name
            parsed_data['name'] = 'Our Market Research Shows That Players Like Really Long Card Names....'
        if 'Ultimate Nightmare' in parsed_data.get('name'):
            # Scryfall includes the stupid ® Character that must be removed
            parsed_data['name'] = 'The Ultimate Nightmare of Wizards of the Coast Customer Service'
        if 'B.F.M.' in parsed_data.get('name'):
            # BFM Halves are not named differently in scryfall
            if parsed_data.get('oracle_id') == '8fd7503b-e722-49a7-a8ac-786e7354bc95':
                parsed_data['name'] = 'B.F.M. (Big Furry Monster) (Left)'
            else:
                parsed_data['name'] = 'B.F.M. (Big Furry Monster) (Right)'
        return ScryfallCard.objects.get_or_create_card(parsed_data)

    @staticmethod
    def get_bulk_data_url():
        url = 'https://api.scryfall.com/bulk-data'
        response = requests.get(url)
        data = json.loads(response._content.decode('utf8')).get('data')
        # We only care about the second bulk object, the "Oracle Cards", which only contains one item per Oracle ID
        for obj in data:
            if obj.get('type') == 'oracle_cards':
                return obj.get('permalink_uri')

    @staticmethod
    def retrieve_bulk_data(url):
        response = requests.get(url)
        return json.loads(response._content.decode('utf8'))
