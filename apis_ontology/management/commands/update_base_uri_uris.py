"""
Update internal project URLs, i.e. entity and relation object Uris, when the
project's APIS_BASE_URI value changes.

Existing project Uris may require updating when APIS_BASE_URI is updated
while the project is still in development. This management command can be
used to replace a given domain name in Uris in the database with the current
value of APIS_BASE_URI. The protocol portion can be left off – "https://"
will be prepended where necessary (replacing instances of the less secure
"http" protocol in any case).
"""

import logging
import re

from apis_core.uris.models import Uri
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import CharField, F, Func, Value

logger = logging.getLogger(__name__)


def normalise_input(val: str) -> str:
    """
    Normalise user-provided string values for domain names.

    If the domain name is prefixed with "http(s)://", the scheme is removed.
    Trailing slashes are also removed.
    """
    v = val.lower().strip().rstrip("/.")
    v = re.sub(r"^https?://", "", v)

    return v


class Command(BaseCommand):
    help = (
        "Replace the domain name portion in project-specific entity and "
        "relation object Uris with the current APIS_BASE_URI value."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "old_base_uri",
            type=str,
            metavar="OLD_BASE_URI",
            help=(
                "Old domain name/URI to be replaced by APIS_BASE_URI in object "
                "Uris. The domain name alone is sufficient – the protocol "
                "portion ('https://') or trailing slashes will be taken "
                "care off automatically."
            ),
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Do not modify the database; show candidate count and sample replacements.",
        )

    def handle(self, *args, **options):
        old_base_uri_raw = options["old_base_uri"]
        dry_run = bool(options.get("dry_run"))

        # verify APIS_BASE_URI is actually set and not empty
        base_uri_setting = getattr(settings, "APIS_BASE_URI", None)
        if not base_uri_setting:
            raise CommandError(
                "APIS_BASE_URI setting is not set or is empty. "
                "Please set it to a valid URL."
            )
        current_base_uri = "https://" + normalise_input(base_uri_setting)

        old_base_uri_domain = normalise_input(old_base_uri_raw)
        # create lookup pattern (string) to fetch Uris with matching
        # domain name + "https" or "http" scheme
        old_base_uri_pattern = (
            r"^(https?://)" + re.escape(old_base_uri_domain) + r"(?=/|$)"
        )

        # exit early if APIS_BASE_URI is the same as the URI that ought to be replaced
        if re.compile(old_base_uri_pattern).match(current_base_uri):
            self.stdout.write(
                "OLD_BASE_URI is identical to APIS_BASE_URI. Nothing to update."
            )
            return

        matching_uris = Uri.objects.filter(uri__iregex=old_base_uri_pattern)
        if (count_uris := matching_uris.count()) == 0:
            self.stdout.write("No matching Uris found.")
            return

        if dry_run:
            sample_size = 5
            self.stdout.write(
                f"Dry run: found {count_uris} relevant Uris. "
                f"Showing up to {sample_size} sample replacements:"
            )
            sample_uris = matching_uris.values_list("uri", flat=True)[:sample_size]

            lookup_pattern = re.compile(old_base_uri_pattern, re.I)
            for uri in sample_uris:
                new_uri = lookup_pattern.sub(current_base_uri, uri)
                self.stdout.write(f"{uri} -> {new_uri}")
            self.stdout.write("Dry run complete. No database changes were made.")
            return

        expr = Func(
            F("uri"),
            Value(old_base_uri_pattern),
            Value(current_base_uri),
            Value("i"),
            function="regexp_replace",
            output_field=CharField(),
        )

        with transaction.atomic():
            updated = matching_uris.update(uri=expr)

        self.stdout.write(f"Processed {count_uris} rows; updated {updated} rows.")
