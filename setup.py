#!/usr/bin/env python
from setuptools import setup, find_packages
import os


# Utility function to read README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-mtg-card-catalog',
    version='0.1',
    description="A reusable django app for syncing the full card and product catalog from TCGPlayer.com's API.",
    author="Scott Johnson",
    author_email='baronvonvaderham@gmail.com',
    url='https://github.com/baronvonvaderham/BayulsBazaar',
    long_description=read("README.md"),
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
    test_suite='tests.main',
    install_requires=['Django', 'celery', 'coverage'],
)
