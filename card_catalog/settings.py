import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '1k6&%=lz&g5br0p6cls@^jv-(5gl22l-z6o&&=3t=&7rd)j)t_'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'celery',
    'card_catalog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# TCGPlayer API Settings
TCG_API_PUBLIC_KEY = os.getenv('TCG_API_PUBLIC_KEY', None)
TCG_API_PRIVATE_KEY = os.getenv('TCG_API_PRIVATE_KEY', None)
TCG_API_APPLICATION_ID = os.getenv('TCG_API_APPLICATION_ID', None)
TCG_AFFILIATE_PARTNER_CODE = os.getenv('TCG_AFFILIATE_PARTNER_CODE', None)

# DATABASE CONFIG
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cardcatalog',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': False
    },
}
REDIS_HOST = os.getenv('REDIS_HOST', 'redis://')

# CELERY
BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_HOST)
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 21600}  # 6 hours
CELERY_APP_NAME = ''
CELERY_RESULT_BACKEND = 'redis://'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ALWAYS_EAGER = os.getenv('CELERY_ALWAYS_EAGER', False)
