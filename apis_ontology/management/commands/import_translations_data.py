import json
import logging

from apis_core.uris.models import Uri
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apis_ontology.models import (
    Expression,
    Group,
    GroupIsPublisherOfManifestation,
    Manifestation,
    ManifestationEmbodiesExpression,
    Person,
    PersonIsAuthorOfWork,
    PersonIsTranslatorOfExpression,
    Work,
    WorkIsRealisedInExpression,
)
from apis_ontology.utils import delete_objects, get_ct

from . import GND_URL, WIKIDATA_URL

logger = logging.getLogger(__name__)

PUBLICATIONS = "data/translations/publications.json"
WORKS = "data/translations/works.json"
TRANSLATIONS = "data/translations/translations.json"
TRANSLATORS = "data/translations/translators.json"


def split_publication_details(input_string: str):
    """
    Split `publication_details` contents into `other_title_information` and
    `pages`.

    The TB in translation key `publication_details` may contain information
    about issues/volumes and/or page references as values. If there is both,
    additional title information comes first, followed by pages, separated
    by a comma.

    Issues or volumes are usually referenced via numbers and/or years and/or
    titles. Occasionally, a full date is given.
    Page references are always prefixed with at least one "S." for "Seiten"
    and can be individual pages or page ranges. Multiple page references are
    separated from one another via slashes; typically (though not reliably),
    subsequent page references are each individually prefixed with "S.".
    Examples: S. 5-8 / 27-84
              36-37, S. 209
              337/5, S. 6-7 / S. 8-11
              7: »Correction«, S. 107-126
    """
    other_title_information = None
    pages = None

    if isinstance(input_string, str):
        combined_info = input_string.split("S.")
        other_title_information = combined_info[0].strip(" ,")

        page_refs = []
        for page_ref in combined_info[1:]:
            # clean up stray slashes and whitespace
            page_ref = page_ref.strip(" /")
            if multiple_refs := page_ref.split("/"):
                # page refs not prefixed with "S." need further splitting up
                for ref in multiple_refs:
                    ref = ref.strip()
                    if ref:
                        page_refs.append(ref)

        pages = "; ".join(page_refs)

    return other_title_information, pages


class Command(BaseCommand):
    help = (
        "Import Works, Persons and Manifestations based on data provided by "
        "Thomas Bernhard in translation project."
    )

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--keep-history", action="store_true")
        parser.add_argument("--models", action="extend", nargs="+")
        parser.add_argument("--fields", action="extend", nargs="+", dest="model_fields")
        parser.add_argument("--values", action="extend", nargs="+", dest="field_values")
        parser.add_argument("--operators", action="extend", nargs="+", dest="operators")

    def handle(self, *args, **options):
        keep_history = options["keep_history"] or False
        dry_run = options["dry_run"] or False

        models = options["models"] or None
        model_fields = options["model_fields"] or None
        field_values = options["field_values"] or None
        operators = options["operators"] or None

        if options["delete"]:
            deleted = delete_objects(
                models=models,
                with_fields=model_fields,
                with_values=field_values,
                operators=operators,
                keep_history=keep_history,
                dry_run=dry_run,
            )
            for qs in deleted:
                logger.debug(qs)

            exit(0)

        # run mgmt command which ensures Thomas Bernhard instance exists
        call_command("create_tb")

        with open(PUBLICATIONS) as f:
            publications = json.load(f)
        with open(TRANSLATIONS) as f:
            translations = json.load(f)
        with open(TRANSLATORS) as f:
            translators = json.load(f)
        with open(WORKS) as f:
            t_works = json.load(f)

        # clean up base data for Persons / TBit translators
        for obj in translators:
            # split translator names into forenames and surnames
            name = obj["name"] or ""
            name_parts = name.split(",", 1)

            obj["surname"] = name_parts[0].strip()
            if len(name_parts) > 1:
                obj["forename"] = name_parts[1].strip()
            else:
                obj["forename"] = ""

        # clean up base data for Works / TBit works
        for obj in t_works:
            tbit_id = obj.get("id")

            # set non-existent title, short_title, category to empty string
            title = obj["title"] or ""
            short_title = obj["short_title"] or ""
            category = obj["category"] or ""

            obj["title"] = title.strip()
            obj["short_title"] = short_title.strip()
            obj["category"] = category.strip()

            # normalise data type for year
            year = obj["year"] or ""

            if year and isinstance(year, int):
                year = str(year)
            elif year and not isinstance(year, str):
                logger.warning(
                    f"Work {title} (tbit_id {tbit_id}) has year of unknown type."
                )
                year = ""

            obj["year"] = year

        # clean up base data for Manifestations / TBit publications
        for obj in publications:
            # set non-existent values empty string
            tbit_id = obj["title"]
            title = obj["title"] or ""
            short_title = obj["short_title"] or ""
            publisher = obj["publisher"] or ""
            language = obj["language"] or ""
            year_display = obj["year_display"] or ""

            obj["title"] = title.strip()
            obj["short_title"] = short_title.strip()
            obj["publisher"] = publisher.strip()
            obj["language"] = language.strip()
            obj["year_display"] = year_display.strip()

            # normalise data type for year
            year = obj["year"] or ""
            if year and isinstance(year, int):
                year = str(year)
            elif year and not isinstance(year, str):
                logger.warning(
                    f"Manifestation {title} (tbit_id {tbit_id}) has year of unknown type."
                )
                year = ""

            obj["year"] = year

            # split publication_details up in manifestation info and pages
            obj["other_title_information"] = ""
            obj["relevant_pages"] = ""

            if pub_details := obj.get("publication_details", None):
                other_title_information, relevant_pages = split_publication_details(
                    pub_details
                )
                if other_title_information:
                    obj["other_title_information"] = other_title_information
                if relevant_pages:
                    obj["relevant_pages"] = relevant_pages

            # items
            obj["item_oeaw"] = False
            obj["item_suhrkamp"] = False

            if obj["exemplar_oeaw"] == "ja":
                obj["item_oeaw"] = True
            if obj["exemplar_suhrkamp_berlin"] == "ja":
                obj["item_suhrkamp"] = True

        # clean up base data for ~ Expressions / TBit translations
        for obj in translations:
            # set non-existent values empty string
            title = obj["title"] or ""
            work_display_title = obj["work_display_title"] or ""

            obj["title"] = title.strip()
            obj["work_display_title"] = work_display_title.strip()

        # add translators / Persons
        # lookup/create instances with GND IDs first
        for translator in [t for t in translators if t["gnd"]]:
            person = None
            gnd = translator["gnd"]
            surname = translator["surname"]
            forename = translator["forename"]

            if gnd.startswith("Q"):
                data_source = WIKIDATA_URL + gnd
            else:
                data_source = GND_URL + gnd

            # check if data uri exists
            if uri := Uri.objects.filter(
                uri=data_source, content_type=get_ct(Person), object_id__isnull=False
            ).first():
                person = uri.content_object

                # (re)import data if this is the only (external) Uri so far (to add more sources)
                if Uri.objects.filter(object_id=uri.object_id).count() <= 2:
                    person = None

            if not person:
                try:
                    person = Person.import_from(data_source)
                except ImproperlyConfigured as e:
                    # sometimes connection to GND fails...
                    logger.error(f"{forename} {surname}: {e}")
                except Exception as e:
                    logger.error(e)
                finally:
                    if not person:
                        for index, item in enumerate(translators):
                            if item["gnd"] == gnd:
                                translators[index]["add_manually"] = True

            if person:
                # prefer TBIT data over existing/newly imported data
                update_fields = []

                if person.surname != surname:
                    update_fields.append("surname")
                    person.surname = surname
                if person.forename != forename:
                    update_fields.append("surname")
                    person.forename = forename

                if update_fields:
                    person.save(update_fields=update_fields)

        # add translators / Persons without GND IDs
        for translator in [
            t for t in translators if not t["gnd"] or t.get("add_manually")
        ]:
            surname = translator["surname"]
            forename = translator["forename"]

            if person := Person.objects.filter(
                surname=surname, forename=forename
            ).first():
                logger.debug(f'Found existing Person "{person}" (ID {person.pk})')
            else:
                person = Person.objects.create(surname=surname, forename=forename)
                logger.debug(f'Person "{person}" created manually (ID {person.pk})')

        # add Works – lookup/create ones with GND IDs first
        for t_work in [tw for tw in t_works if tw["gnd"]]:
            work = None
            tbit_id = t_work["id"]
            gnd = t_work["gnd"]
            title = t_work["title"]
            short_title = t_work["short_title"]
            tbit_category = t_work["category"]
            year = t_work["year"]

            if gnd.startswith("Q"):
                data_source = WIKIDATA_URL + gnd
            else:
                data_source = GND_URL + gnd

            # check if data uri exists
            if uri := Uri.objects.filter(
                uri=data_source,
                content_type=get_ct(Work),
                object_id__isnull=False,
            ).first():
                work = uri.content_object

            if not work:
                try:
                    work = Work.import_from(data_source)
                except ImproperlyConfigured as e:
                    # sometimes connection to GND fails...
                    logger.error(f"{title}: {e}")
                except Exception as e:
                    logger.error(e)
                finally:
                    if not work:
                        for index, item in enumerate(t_works):
                            if item["gnd"] == gnd:
                                t_works[index]["add_manually"] = True

            if work:
                # prefer TBIT data over existing/newly imported data
                update_fields = []

                if work.title != title:
                    update_fields.append("title")
                    work.title = title

                if work.tbit_category != tbit_category:
                    update_fields.append("tbit_category")
                    work.tbit_category = tbit_category

                # save TBIT short_title to other_title_information field
                if short_title and short_title not in work.other_title_information:
                    update_fields.append("other_title_information")
                    if work.other_title_information:
                        work.other_title_information += f" (short title: {short_title})"
                    else:
                        work.other_title_information = f"(short title: {short_title})"

                if update_fields:
                    work.save(update_fields=update_fields)

        # add Works without GND IDs
        for t_work in [tw for tw in t_works if not tw["gnd"] or tw.get("add_manually")]:
            tbit_id = t_work["id"]
            title = t_work["title"]
            short_title = t_work["short_title"]
            tbit_category = t_work["category"]
            year = t_work["year"]

            if work := Work.objects.filter(title=title).first():
                logger.debug(f'Found existing Work "{work}" (ID {work.pk})')
            else:
                work = Work.objects.create(
                    title=title,
                    tbit_category=tbit_category,
                )
                logger.debug(f'Work "{work}" created manually (ID {work.pk})')

            update_fields = []

            if work.tbit_category != tbit_category:
                update_fields.append("tbit_category")
                work.tbit_category = tbit_category

            if short_title and short_title not in work.other_title_information:
                update_fields.append("other_title_information")
                if work.other_title_information:
                    work.other_title_information += f" (short title: {short_title})"
                else:
                    work.other_title_information = f"(short title: {short_title})"

            if update_fields:
                work.save(update_fields=update_fields)

            author = Person.objects.filter(
                forename="Thomas", surname="Bernhard"
            ).first()
            is_author, created = PersonIsAuthorOfWork.objects.get_or_create(
                subj_object_id=author.pk,
                obj_object_id=work.pk,
                subj_content_type=get_ct(Person),
                obj_content_type=get_ct(Work),
            )

        # add publications / Manifestations first, then retrieve
        # related Expressions and Works from translations data
        for pub in [p for p in publications]:
            manif_title = pub["title"]
            manif_short_title = pub["short_title"]
            manif_year = pub["year"]

            signatur = pub["signatur"]
            publisher = pub["publisher"]
            other_title_info = pub["other_title_information"]
            pages = pub["relevant_pages"]

            exp_language = pub["language"]
            contained_trans = pub["contains"]  # lists of integers

            if manifestation := Manifestation.objects.filter(
                title=manif_title, tbit_shelfmark=signatur
            ).first():
                pass
            elif manifestation := Manifestation.objects.filter(
                title=manif_title
            ).first():
                pass
            elif manifestation := Manifestation.objects.create(
                title=manif_title,
                other_title_information=other_title_info,
                publication_date=manif_year,
                tbit_shelfmark=signatur,
                relevant_pages=pages,
            ):
                pass

            manif_update_fields = []
            if (
                other_title_info
                and other_title_info not in manifestation.other_title_information
            ):
                manif_update_fields.append("other_title_information")
                manifestation.other_title_information = other_title_info
            if signatur and manifestation.tbit_shelfmark != signatur:
                manif_update_fields.append("tbit_shelfmark")
                manifestation.tbit_shelfmark = signatur
            if pages and manifestation.relevant_pages != pages:
                manif_update_fields.append("relevant_pages")
                manifestation.relevant_pages = pages

            if manif_update_fields:
                manifestation.save(update_fields=manif_update_fields)

            if (
                manif_short_title
                and manif_short_title not in manifestation.other_title_information
            ):
                if manifestation.other_title_information:
                    manifestation.other_title_information += (
                        f" (short title: {manif_short_title})"
                    )
                else:
                    manifestation.other_title_information = (
                        f"(short title: {manif_short_title})"
                    )
                manifestation.save(update_fields=["other_title_information"])

            if publisher:
                group = Group.objects.filter(label=publisher).first()
                if not group:
                    group = Group.objects.create(label=publisher)

                group_is_publisher, created = (
                    GroupIsPublisherOfManifestation.objects.get_or_create(
                        subj_object_id=group.pk,
                        obj_object_id=manifestation.pk,
                        subj_content_type=get_ct(Group),
                        obj_content_type=get_ct(Manifestation),
                    )
                )

            for trans_id in contained_trans:
                matching_exp = [item for item in translations if item["id"] == trans_id]

                for exp in matching_exp:
                    exp_title = exp["title"]
                    translator_ids = exp["translators"] or []
                    work_id = exp["work"] or ""

                    if expression := Expression.objects.filter(
                        title=exp_title, language=exp_language
                    ).first():
                        pass
                    elif expression := Expression.objects.filter(
                        title=exp_title
                    ).first():
                        pass
                    else:
                        expression = Expression.objects.create(
                            title=exp_title, language=language
                        )

                    manif_embodies_expr, created = (
                        ManifestationEmbodiesExpression.objects.get_or_create(
                            subj_object_id=manifestation.pk,
                            obj_object_id=expression.pk,
                            subj_content_type=get_ct(Manifestation),
                            obj_content_type=get_ct(Expression),
                        )
                    )

                    related_work = [item for item in t_works if item["id"] == work_id][
                        0
                    ]
                    work = Work.objects.filter(
                        title=related_work["title"],
                        tbit_category=related_work["category"],
                    ).first()

                    work_realised_in_exp, created = (
                        WorkIsRealisedInExpression.objects.get_or_create(
                            subj_object_id=work.pk,
                            obj_object_id=expression.pk,
                            subj_content_type=get_ct(Work),
                            obj_content_type=get_ct(Expression),
                        )
                    )

                    related_translators = [
                        item for item in translators if item["id"] in translator_ids
                    ]
                    for t in related_translators:
                        person = Person.objects.filter(
                            forename=t["forename"],
                            surname=t["surname"],
                        ).first()

                        if person:
                            is_translator, created = (
                                PersonIsTranslatorOfExpression.objects.get_or_create(
                                    subj_object_id=person.pk,
                                    obj_object_id=expression.pk,
                                    subj_content_type=get_ct(Person),
                                    obj_content_type=get_ct(Expression),
                                )
                            )
