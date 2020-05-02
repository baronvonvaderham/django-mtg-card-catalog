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
    'Corpse Knight Reminder Card',
    'Brawl Deck',
    'Challenge Deck',
    'Guild Kit',
    'Fire and Lightning Deck',
    'Planeshift - ',
    'Planechase 2012 - ',
    'Planechase 2009 - ',
    'Magic Game Night',
    'Start Deck',
    'Land Station',
    'Commander - ',
    'Deluxe Collection',
    'Endgame Set',
    'Secret Lair Drop:',
    'Secret Lair: Ultimate Edition Box',
    'SDCC 2014 Exclusive M15 Black Planeswalkers w/ Axe',
    # Some nonsense SUM cards suddenly appeared one day
    'Artifact of Mishra',
    "Jandor's Mage",
    "Mon's Goblin Raiders",
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
    # The "test print" cards are just obnoxious, excluding unless a user requests them
    'Mystery Booster: Convention Edition Exclusives'
]

GODZILLA_MAPPER = {
    'Bio-Quartz Spacegodzilla': 'Brokkos, Apex of Forever',
    'Rodan, Titan of Winged Fury': 'Vadrok, Apex of Thunder',
    'Biollante, Plant Beast Form': 'Nethroi, Apex of Death',
    'Ghidorah, King of the Cosmos': 'Illuna, Apex of Wishes',
    'King Caesar, Awoken Titan': 'Snapdax, Apex of the Hunt',
    'Godzilla, Primeval Champion': 'Titanoth Rex',
    'Godzilla, Doom Inevitable': 'Yidaro, Wandering Monster',
    'Destoroyah, Perfect Lifeform': 'Everquill Phoenix',
    'Mothra, Supersonic Queen': 'Luminous Broodmoth',
    'Gigan, Cyberclaw Terror': 'Gyruda, Doom of Depths',
    'Spacegodzilla, Void Invader': 'Void Beckoner',
    'Spacegodzilla, Death Corona': 'Void Beckoner',
    'Anguirus, Armored Killer': 'Gemrazer',
    'King Caesar, Ancient Guardian': 'Huntmaster Liger',
    'Dorat, the Perfect Pet': 'Sprite Dragon',
    'Babygodzilla, Ruin Reborn': 'Pollywog Symbiote',
    'Godzilla, King of the Monsters': 'Zilortha, Strength Incarnate',
    'Battra, Terror of the City': 'Dirge Bat',
    'Mechagodzilla, the Weapon': 'Crystalline Giant',
    'Mechagodzilla': 'Crystalline Giant',
    'Mothra\'s Giant Cocoon': 'Mysterious Egg',
}

# A mapper to correct incredibly stupid typos in TCGPlayer's database
STUPID_TCGPLAYER_TYPO_MAPPER = {
    'Nezumi Shortfang // Nezumi Shortfang': 'Nezumi Shortfang // Stabwhisker the Odious',
    'Nezumi Graverobber / Nighteyes the Desecrator': 'Nezumi Graverobber // Nighteyes the Desecrator',
    'Grisly Savage': 'Grisly Salvage',
    'Wyden the Biting Gale': 'Wydwen, the Biting Gale',
}
