MtgCardCatalog [![Build Status](https://travis-ci.org/baronvonvaderham/django-mtg-card-catalog.svg?branch=master)](https://travis-ci.org/baronvonvaderham/django-mtg-card-catalog) [![Coverage Status](https://coveralls.io/repos/github/baronvonvaderham/django-mtg-card-catalog/badge.svg?branch=master)](https://coveralls.io/github/baronvonvaderham/django-mtg-card-catalog?branch=master)
================
A reusable django app for syncing the full card and product catalog from TCGPlayer.com's API.

Also includes a Scryfall API service for augmenting TCGPlayer card data with additional useful attributes (e.g. CMC, color, types)

Installation
---------------
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
-------------
Required settings:
* TCG_API_PUBLIC_KEY (str)
* TCG_API_PRIVATE_KEY (str)
* TCG_API_APPLICATION_ID (int)
* TCG_AFFILIATE_PARTNER_CODE (str)

These are the credentials that were provided to you by TCGPlayer when your application for API access was approved. Which value goes where is pretty self-evident.


Usage
-----

Models, services, and tasks can be accessed directly (TODO: add explicit documentation for each). In most cases, you will be referencing a Card, CardSet, CardPrice, etc. as a ForeignKey on your own models to easily attach the relevant data.

Sync tasks are currently hard-coded with run times to fit TCGPlayer's recommended windows for retrieving data. This will be updated to be configurable in a later release.
