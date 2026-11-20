"""
Identify Manifestation objects derived from TBit data whose publication_date
field contains a value, but whose related fuzzy date fields – i.e.
publication_date_date_from, publication_date_date_sort, publication_date_date_to –
remain unset, and call .save() on them invididually to populate the fields.

This is useful for Manifestation objects which were imported from TBit data,
whose publication_date was set (based on TBit's publication "year" value),
but for which the relevant FuzzyDateParserField logic did not run.

Objects without a publication date are skipped, as are objects with non-emtpy
values for any of the fuzzy date fields, so as not to overwrite existing data.
"""

import logging

from django.core.management.base import BaseCommand

from apis_ontology.models import Manifestation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Add TBit language data to Manifestation objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write changes. Without this option, only report planned changes.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        if not apply_changes:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be saved")
            )

        # only process Manifestation objects which derive from TBit data
        # (i.e. have tbit_shelfmark set)
        manifestations = Manifestation.objects.exclude(tbit_shelfmark="")
        count_manif = manifestations.count()
        self.stdout.write(
            f"Found {count_manif} Manifestation objects with tbit_shelfmark set."
        )

        updated_count = 0
        skipped_count_missing_pubdate = 0
        skipped_count_has_fuzzyfields = 0
        error_count = 0
        warning_count = 0

        for m in manifestations:
            m_id = m.id
            title = m.title
            tbit_shelfmark = m.tbit_shelfmark
            publication_date = m.publication_date
            publication_date_date_from = m.publication_date_date_from
            publication_date_date_sort = m.publication_date_date_sort
            publication_date_date_to = m.publication_date_date_to

            # ignore Manifestation objects which do not have a publication date
            # set to begin with
            if not publication_date:
                skipped_count_missing_pubdate += 1
                logger.debug(
                    f"No publication date found for Manifestation ID {m_id} "
                    f"('{title}', {tbit_shelfmark})"
                )
                continue

            # ignore Manifestation objects which already have any of the
            # fuzzy date fields for publication_date set (so as not to
            # overwrite existing data)
            if (
                publication_date_date_from
                or publication_date_date_sort
                or publication_date_date_to
            ):
                skipped_count_has_fuzzyfields += 1
                logger.debug(
                    f"Skipping Manifestation ID {m_id} ('{title}', {tbit_shelfmark}) "
                    f"because it already has (some) fuzzy date fields for "
                    f"publication_date set"
                )
                continue

            # update applicable Manifestation objects if --apply argument was
            # provided, otherwise only report what would be updated
            if apply_changes:
                try:
                    m.publication_date = publication_date
                    m._change_reason = "backfill: tbit manifestations publication_date fuzzy date fields"
                    m.save()
                    updated_count += 1
                    self.stdout.write(
                        f"Updated Manifestation ID {m_id} ('{title}', {tbit_shelfmark}) "
                        f"with publication date: {publication_date}"
                    )
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error updating Manifestation ID {m_id} "
                            f"('{title}', {tbit_shelfmark}): {e}"
                        )
                    )
            else:
                updated_count += 1
                self.stdout.write(
                    f"[DRY RUN] Would update Manifestation ID {m_id} ('{title}', {tbit_shelfmark}) "
                    f"with publication date: {publication_date}"
                )

        # summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))

        if not apply_changes:
            self.stdout.write(self.style.WARNING("DRY RUN Summary:"))
        else:
            self.stdout.write(self.style.SUCCESS("Summary:"))

        self.stdout.write(f"  Total Manifestations: {count_manif}")
        self.stdout.write(self.style.SUCCESS(f"  Updated:  {updated_count}"))
        self.stdout.write(
            self.style.WARNING(
                f"  Skipped:  {skipped_count_missing_pubdate + skipped_count_has_fuzzyfields}"
            )
        )
        if skipped_count_missing_pubdate > 0:
            self.stdout.write(
                f"        ... {skipped_count_missing_pubdate} objects without publication_date"
            )
        if skipped_count_has_fuzzyfields > 0:
            self.stdout.write(
                f"        ... {skipped_count_has_fuzzyfields} objects with non-empty fuzzy date fields"
            )

        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  Errors:   {error_count}"))
        if warning_count > 0:
            self.stdout.write(self.style.WARNING(f"  Warnings: {warning_count}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
