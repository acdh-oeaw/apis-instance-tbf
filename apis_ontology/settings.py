"""
Settings for apis_ontology Django project.

Variables are grouped by:
- Django general settings/built-ins
- configs for third-party dependencies
- APIS-specific variables
- custom project settings
"""

from apis_acdhch_default_settings.settings import *

# Django general settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Application definition

APIS_APPS_PREPEND = ["apis_core.relations"]
APIS_APPS_APPEND = [
    "apis_core.history",
    "apis_core.documentation",
]

for a in APIS_APPS_PREPEND:
    if a not in INSTALLED_APPS:
        INSTALLED_APPS.insert(0, a)

for a in APIS_APPS_APPEND:
    if a not in INSTALLED_APPS:
        INSTALLED_APPS.append(a)


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

# django-tables2 settings
DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-hover table-striped",
    "thead": {
        "class": "table-light",
    },
}

# APIS-specific settings
GIT_REPOSITORY_URL = "https://github.com/acdh-oeaw/apis-instance-tbf"
