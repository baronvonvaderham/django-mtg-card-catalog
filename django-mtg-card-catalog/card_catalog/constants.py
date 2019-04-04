# -*- coding: utf-8 -*-
TCG_BEARER_TOKEN_URL = 'https://api.tcgplayer.com/token'
TCG_ALL_SETS_URL = 'http://api.tcgplayer.com/catalog/groups'
TCG_CARD_LIST_FOR_SET_URL = 'http://api.tcgplayer.com/catalog/products'
TCG_PRICES_FOR_SET_URL = 'http://api.tcgplayer.com/v1.19.0/pricing/group/{}'
SCRYFALL_NAMED_CARD_LOOKUP_URL = 'https://api.scryfall.com/cards/named'

BASIC_TYPES = [
    'Swamp',
    'Plains',
    'Island',
    'Forest',
    'Mountain',
    'Wastes',
]

EXCLUDED_CARD_NAMES = [
    'Booster Box',
    'Booster Pack',
    'Fat Pack',
    'Box Set',
    'Theme Deck',
    'Planeswalker Deck',
    'Token',
    'Prerelease Kit',
    'Starter Deck',
    'Holiday Box',
    'Checklist',
    'Gift Box',
    'Emblem',
    'Booster Battle Pack',
    'Tournament Pack',
    'Intro Packs',
    'Intro Pack',
    'Gift Pack',
    'Display',
    'Set of',
    'Deck Builder',
    'Event Deck',
    'Prerelease',
    'Theme',
    'Duel Deck',
    'Clash Pack',
    'Deckmasters',
    'Boxed',
    # Covers all commander decks since they all contain stuff like 'Commander 2018'
    'Commander 20',
    'Challenger Deck',
    'Starter Kit',
    'Rules Card',
    '2 Player',
    'Starter Set'
    'Playmat',
    'Premium Deck Series',
    'Magic Game Night Set',
    'International',
    'Bundle',
    'Planeswalker Set',
    'Planeswalkers Set',
    'Global Series',
    'Experience Card',
    # Of course the BNG decks need to be named differently from any other set
    'Born of the Gods',
    "Collectors' Edition Box",
    'Booster Draft Pack',
    'Hascon Collection',
    'Rise of the Eldrazi',
    'Two-Player',
    'Mythic Edition',
    # Of course the 2014 SDCC set had to be named completely differently from the rest and require a unique exclusion
    'SDCC 2014 EXCLUSIVE',
]

EXCLUDED_SETS = [
    'World Championship Decks',
    'Duel Decks',
    'Duels of the Planeswalkers',
    'Astral',
    'Guilds of Ravnica: Guild Kits',
    'Explorers of Ixalan',
    'JingHe Age Token Cards',
    'Magic Premiere Shop',
    'Oversize Cards',
    'Box Sets',
]
