"""
Settings for apis_ontology Django project.

Variables are grouped by:
- Django general settings/built-ins
- configs for third-party dependencies
- APIS-specific variables
- custom project settings
"""

from apis_acdhch_default_settings.settings import *
from django.utils.translation import gettext_lazy as _

# Django general settings

# Core settings
# https://docs.djangoproject.com/en/stable/ref/settings/#core-settings

DEBUG = False

INSTALLED_APPS += [
    app
    for app in [
        "apis_core.documentation",
        "django_interval",
    ]
    if app not in INSTALLED_APPS
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600),
}

ROOT_URLCONF = "apis_ontology.urls"

WSGI_APPLICATION = "apis_ontology.wsgi.application"

# Internationalization-specific settings
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "de-at"

LANGUAGES = [
    ("de", _("German")),
]

TIME_ZONE = "CET"

# Django plugins / third-party dependencies settings

# django-tables2 config
DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-hover table-striped",
    "thead": {
        "class": "table-light",
    },
}

# Django REST framework config
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.IsAuthenticatedOrReadOnly",
)

# APIS framework-specific variables

GIT_REPOSITORY_URL = "https://github.com/acdh-oeaw/apis-instance-tbf"
