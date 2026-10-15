"""
Add TBit language data to existing Manifestation objects previously imported
from publications.json.

Identifies relevant Manifestation object instances by their "tbit_shelfmark"
field value, then sets the "primary_language" and "language_variety" fields
based on the "language" value in the TBit JSON.
"""

import logging

from django.core.management.base import BaseCommand

from apis_ontology.models import Manifestation
from apis_ontology.utils import (
    get_matching_language_variety_code,
    get_matching_primary_language_code,
    load_json_file,
    split_tbit_language_tag,
)

from .utils import TBIT_PUBLICATIONS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add TBit language data to Manifestation objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not modify the database; show what would be updated "
            "without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be saved")
            )

        publications = load_json_file(TBIT_PUBLICATIONS)

        if not publications:
            self.stdout.write(self.style.ERROR(f"File not found: {TBIT_PUBLICATIONS}"))
            return

        self.stdout.write(f"Found {len(publications)} publications in JSON.")

        # create publications lookup dictionary: signatur -> language
        pub_sig_lang_lookup = {}
        for pub in publications:
            signatur = pub.get("signatur")
            language = pub.get("language")
            if signatur and language:
                pub_sig_lang_lookup[signatur] = language

        self.stdout.write(
            f"Built publications lookup table with {len(pub_sig_lang_lookup)} signatur-language pairs"
        )

        # process Manifestation objects which derive from TBit data (have tbit_shelfmark set)
        manifestations = Manifestation.objects.exclude(tbit_shelfmark="")
        count_manif = manifestations.count()
        self.stdout.write(
            f"Found {count_manif} Manifestation objects with tbit_shelfmark set."
        )

        updated_count = 0
        skipped_count = 0
        error_count = 0
        warning_count = 0

        for m in manifestations:
            m_id = m.id
            title = m.title
            tbit_shelfmark = m.tbit_shelfmark

            language = pub_sig_lang_lookup.get(tbit_shelfmark)

            if not language:
                skipped_count += 1
                logger.debug(
                    f"No language data found for Manifestation ID {m_id} ('{title}') "
                    f"in TBit publication with signatur {tbit_shelfmark}."
                )
                continue

            # parse language value, e.g. "fr" or "pt_br" or "zh_hans"
            primary_language_raw, language_variety_raw = split_tbit_language_tag(
                language
            )

            if not primary_language_raw:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not parse language '{language}' for {tbit_shelfmark}"
                    )
                )
                error_count += 1
                continue

            # update Manifestation object primary_language and language_variety value
            try:
                primary_language = get_matching_primary_language_code(
                    primary_language_raw
                )
                language_variety = (
                    get_matching_language_variety_code(language_variety_raw)
                    if language_variety_raw
                    else ""
                )

                if language_variety_raw and not language_variety:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not find matching language variety for '{language_variety_raw}'"
                        )
                    )
                    warning_count += 1
                    continue

                if not dry_run:
                    m.primary_language = primary_language
                    m.language_variety = language_variety
                    m.save(update_fields=["primary_language", "language_variety"])

                updated_count += 1
                self.stdout.write(
                    f"{'[DRY RUN] Would update' if dry_run else 'Updated'} "
                    f"Manifestation ID {m_id} ('{title}') with primary_language: {primary_language}"
                    f"{', language variety: ' + language_variety if language_variety else ''}"
                )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error updating Manifestation '{title}' (ID {m_id}): {e}"
                    )
                )

        # summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(
            self.style.SUCCESS(f"{'DRY RUN ' if dry_run else ''}Summary:")
        )
        self.stdout.write(f"  Total Manifestations: {count_manif}")
        self.stdout.write(self.style.SUCCESS(f"  Updated: {updated_count}"))
        self.stdout.write(
            self.style.WARNING(f"  Skipped (no language data): {skipped_count}")
        )
        if error_count > 0 or warning_count > 0:
            self.stdout.write(self.style.ERROR(f"  Errors: {error_count}"))
        if warning_count > 0:
            self.stdout.write(self.style.ERROR(f"  Warnings: {warning_count}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
