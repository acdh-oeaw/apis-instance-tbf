"""
Settings for "Thomas Bernhard online" Django project.

Variables are grouped by:
- Django general settings, i.e. overrides of django/conf/global_settings
  and django/contrib apps,
- third-party dependencies/Django plugins configs,
- APIS app-specific variables (i.e. apis_core & related),
- custom project variables.
"""

from apis_acdhch_default_settings.settings import *
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

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

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

# Internationalization-specific settings
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "de-at"

LANGUAGES = [
    ("de", _("German")),
]

TIME_ZONE = "CET"

# Static file settings
# https://docs.djangoproject.com/en/stable/ref/settings/#static-files

STATIC_ROOT = BASE_DIR / "static_files"
STATIC_URL = "static/"


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

# Custom project variables

# path to directory holding RDF import configs
RDF_CONFIG_ROOT = BASE_DIR / "apis_ontology" / "triple_configs"
