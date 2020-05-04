MtgCardCatalog [![Build Status](https://travis-ci.org/baronvonvaderham/django-mtg-card-catalog.svg?branch=master)](https://travis-ci.org/baronvonvaderham/django-mtg-card-catalog) [![Coverage Status](https://coveralls.io/repos/github/baronvonvaderham/django-mtg-card-catalog/badge.svg?branch=master)](https://coveralls.io/github/baronvonvaderham/django-mtg-card-catalog?branch=master)
================
A reusable django app for syncing the full card and product catalog from TCGPlayer.com's API.

Also includes a Scryfall API service for augmenting TCGPlayer card data with additional useful attributes (e.g. CMC, color, types)

Installation
============
1. Add to your requirements.txt:
```
-e git://github.com/baronvonvaderham/django-mtg-card-catalog@master#egg=django-mtg-card-catalog
```

2. Add to your INSTALLED_APPS setting:
```
'celery',
'card_catalog'
```

3. Run "pip install -r requirements.txt" from your project's directory to install required packages.

4. Run "python manage.py migrate" to create the required models.

Configuration
=============
Required settings:
* TCG_API_PUBLIC_KEY (str)
* TCG_API_PRIVATE_KEY (str)
* TCG_API_APPLICATION_ID (int)
* TCG_AFFILIATE_PARTNER_CODE (str)

These are the credentials that were provided to you by TCGPlayer when your application for API access was approved. Which value goes where is pretty self-evident.


Usage
=====

Models, services, and tasks can be accessed directly. In most cases, you will be referencing a Card, CardSet, CardPrice, etc. as a ForeignKey on your own models to easily attach the relevant data, and will just need to set up a celery beat schedule to run the sync tasks automatically to keep these tables up to date.

Tasks
-----
These are the core tasks that must be added to your app's celery beat schedule. There are other "minor" tasks that are called by these but should not be called directly.

* ScryfallSyncTask
    * Task Name: `scryfall-sync-task`
    * Function: Retrieves all cards from Scryfall's API in a single query, then processes them to create ScryfallCard models containing data such as CMC, colors, etc. to augment the TCGPlayer Card model
* SetSyncTask
    * Task Name: `set-sync-task`
    * Function: Queries TCGPlayer's API for a list of all printed sets then creates any new sets it does not find already in the database
* CardSyncTask
    * Task Name: `card-sync-task`
    * Function: Queries all card sets in the database, then for each set queries the TCGPlayer API for a list of all products for that set
    * Arguments: `sync_all_products` - Boolean to be passed into task indicating whether to sync cards only (False) or all products (True) such as booster packs and theme decks
* PriceSyncTask
    * Task Name: `price-sync-task` 
    * Function: Queries all card sets in the database, then for each set queries the TCGPlayer API for prices for each product for that set

Schedule
--------

A simple celery beat schedule is all that is needed to make use of these tasks. This is a single entry added to your project's settings file.

TCGPlayer requests that all price syncing happen only once daily between the hours of 3am and 7am eastern, please construct your schedule accordingly. Here is a suggested schedule:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "scryfall-sync-task": {
        "task": "scryfall-sync-task",
        "schedule": crontab(hour=3, minute=30)
    },
    "set-sync-task": {
        "task": "set-sync-task",
        "schedule": crontab(hour=3, minute=45)
    },
    "card-sync-task": {
        "task": "card-sync-task",
        "schedule": crontab(hour=4, minute=0),
        "kwargs": {'sync_all_products': True}  ## Optional
    },
    "price-sync-task": {
        "task": "price-sync-task",
        "schedule": crontab(hour=4, minute=30)
    },
}
```

Additional documentation on Celery task scheuling can be found at: http://docs.celeryproject.org/en/v2.3.3/userguide/periodic-tasks.html
