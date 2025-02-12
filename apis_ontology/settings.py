"""
Django settings for apis_ontology project.
"""

from apis_acdhch_default_settings.settings import *

# Django general settings

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += ["apis_core.history"]
INSTALLED_APPS = ["apis_core.relations"] + INSTALLED_APPS
INSTALLED_APPS += ["apis_core.documentation"]

# Application definition

WSGI_APPLICATION = "apis_ontology.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600),
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "de-at"

TIME_ZONE = "CET"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Third-party dependencies

# Content Security Policy settings
# TODO remove variable once it has been added to apis-acdhch-default-settings
CSP_FRAME_ANCESTORS = ["https://*.pages.oeaw.ac.at/"]


# APIS-specific settings
GIT_REPOSITORY_URL = "https://github.com/acdh-oeaw/apis-instance-tbf"
