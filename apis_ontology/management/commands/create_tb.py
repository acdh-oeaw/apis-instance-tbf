"""
Creates a Person object instance for Thomas Bernhard if there isn't one yet.

Attempts to populate fields with GND data on initial creation (or queries
Wikidata as fallback). Raises an error if everything fails.

Meant to be called by all management commands which import project data.
"""

import logging

from apis_core.uris.models import Uri
from django.core.management.base import BaseCommand, CommandError

from apis_ontology.importers import PersonImporter
from apis_ontology.models import Person

from . import GND_URL, TB_GND_ID, TB_WD_ID, WIKIDATA_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates a Person instance for Thomas Bernhard if there isn't one yet."

    def handle(self, *args, **options):
        tb = None

        tb_gnd_uri = GND_URL + TB_GND_ID
        tb_wikidata_uri = WIKIDATA_URL + TB_WD_ID

        if uri := Uri.objects.filter(uri=tb_gnd_uri).first():
            tb = uri.content_object
            logger.debug(f'Person instance "{tb}" already exists (ID {tb.pk}).')
        else:
            try:
                # sometimes connection to GND fails...
                tb = PersonImporter(tb_gnd_uri, Person).create_instance()
                logger.debug(f'Imported Person instance "{tb}" (ID {tb.pk}).')
            except Exception as e:
                logger.error(e)
                logger.warning(f"Could not fetch data from ({tb_gnd_uri}).")

                tb = Person.objects.filter(
                    forename="Thomas", surname="Bernhard"
                ).first()
                if not tb:
                    tb = Person.objects.create(forename="Thomas", surname="Bernhard")
                    logger.debug(
                        f'Created Person instance "{tb}" manually (ID {tb.pk}).'
                    )

                # try to enrich with data from Wikidata as fallback
                try:
                    tb = PersonImporter(tb_wikidata_uri, Person).create_instance()
                except Exception as e:
                    logger.error(e)
                    logger.warning(f"Could not fetch data from ({tb_wikidata_uri}).")

        if not tb:
            raise CommandError(
                "Could neither fetch data for nor manually create Person instance for Thomas Bernhard."
            )
