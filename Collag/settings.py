"""
Django settings for Collag project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sjcahn0zcb_fg2a*086l702ju)h2@#wonk20(52#7slzt3)ng#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'collage',



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

ROOT_URLCONF = 'Collag.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # -- added by nenu 12.04.2019
            ],
        },
    },
]

WSGI_APPLICATION = 'Collag.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Authorization
# https://docs.djangoproject.com/es/2.0/topics/auth/

# ГОВОРИМ джанге, какую модель использовать для авторизации:

#урл для авторизации

#куда редиректим после авторизации


# Говорим как производится авторизациия
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'



GLOBAL_SETTINGS = {
    'FLICKR_PUBLIC': '1f9874c1a8ea5a85acfd419dd0c2c7e1',
    'FLICKR_SECRET': '67de04d2825fd397',
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Celery settings

CELERY_BROKER_URL = 'redis://localhost'
#
# #: Only add pickle to this list if your broker is secured
# #: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False

#
#
#
# # Redis settings:
#
REDIS_BACKEND = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
}
#
REDIS_BACKEND_URL = 'redis://{host}:{port}/{db}'.format(
    host=REDIS_BACKEND['HOST'],
    port=REDIS_BACKEND['PORT'],
    db=REDIS_BACKEND['DB'],
)
#
#
# # CELERY SETTINGS
#
# # If you want to use Redis for storing results (probably not):
# # CELERY_RESULT_BACKEND = 'redis://{host}:{port}/{db}'.format(
# #     host=REDIS_BACKEND['HOST'],
# #     port=REDIS_BACKEND['PORT'],
# #     db=REDIS_BACKEND['DB'],
# # )
#
#
# BROKER_URL = REDIS_BACKEND_URL
#
# # Periodic tasks:
# CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# Email settings
# https://medium.com/@_christopher/how-to-send-emails-with-python-django-through-google-smtp-server-for-free-22ea6ea0fb8e
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_PORT = 465  # 465 - SSL; 587 - TSL
EMAIL_HOST_USER = 'nenuzhny112018@gmail.com'
EMAIL_HOST_PASSWORD = 'nenu32590632'