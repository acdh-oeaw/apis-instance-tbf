import json
import logging

from apis_core.apis_entities.utils import get_entity_classes
from apis_core.uris.models import Uri
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apis_ontology.importers import GroupImporter, PersonImporter, WorkImporter
from apis_ontology.models import (
    Event,
    EventHadParticipantGroup,
    EventHadParticipantPerson,
    Group,
    Performance,
    PerformanceHadDirectorPerson,
    PerformanceHadParticipantGroup,
    PerformanceHadParticipantPerson,
    PerformancePerformedWork,
    Person,
    Poster,
    PosterPromotedEvent,
    PosterPromotedPerformance,
    Work,
)
from apis_ontology.utils import delete_objects, get_ct, get_relation_classes

from . import GND_URL

logger = logging.getLogger(__name__)

OPENREFINE_EXPORT = "data/posters/FTB_posters_initial_catalogue_refined.json"


def add_text(text_value, new_text):
    """
    Add text to a variable holding content for a text field separating
    existing content from new text with a newline.

    If the variable is falsy (it may originally be set to None), set it
    to an empty string.
    """
    if text_value:
        text_value += "\n"
    else:
        text_value = ""
    text_value += new_text
    return text_value


def extract_gnd_refs(data_object, exclude_types=None):
    """
    Return only the GND-related portion of an object's data for objects
    which were linked with the GND in OpenRefine.

    The GND refs are the value of an object's "match" key or included in
    a list of "candidates".
    Example for relevant data:
        {
          "id": "4221007-0",
          "name": "Heldenplatz",
          "types": ["AuthorityResource","Work"],
          "score": 74.80832
        }

    If there is no "match" but there are "candidates", the highest scoring
    candidate's GND metadata is returned.
    The optional "exclude_types" argument can be used to exclude candidates
    of a certain entity type.

    :param data_object: a full data object
    :type data_object: dict
    :param exclude_types: entity types to exclude when looking for the highest
                          scoring candidate (types used by the GND, including
                          "Works", "DifferentiatedPerson", "CorporateBody")
    :type exclude_types: list of strings
    :return: a dictionary with GND-related references
    :rtype: list
    """
    gnd_refs = []

    if data_object["match"]:
        gnd_refs.append(data_object["match"])
    elif data_object["candidates"]:
        # use candidate with the highest score
        candidates = data_object["candidates"]
        best_candidate = max(
            [c for c in candidates if exclude_types not in c["types"]],
            key=lambda x: x["score"],
        )
        gnd_refs.append(best_candidate)
    else:
        pass

    return gnd_refs


def split_people(raw_data):
    """
    Convert strings which may contain the names of multiple people
    into a list of strings.

    Split raw data by semicolons to separate multiple people from one another,
    then further separate resulting substrings into forenames and surnames
    (where applicable).

    :param people: an input string
    :type people: str
    :return: a list of names formatted SURNAME, FORENAME
    :rtype: list
    """
    names = []

    people = raw_data.split(";")
    for val in people:
        full_name = val.split(",", 1)
        surname = full_name[0].strip()
        try:
            forename = full_name[1].strip()
        except IndexError:
            forename = ""
        names.append((surname, forename))

    return names


def convert_placeholder_dates(date_string):
    """
    Remove placeholder characters from partial string representations
    of ISO dates.

    :param date_string: a string which might look like an ISO date, or an
                        ISO date with the character "x" in place of some of
                        the date information, e.g. 1972-xx-xx or 1980-02-xx
    :type date_string: str
    :return: the date string but with all placeholder characters removed
    :rtype: str
    """

    while len(date_string) > 0 and "x" in date_string[-1]:
        date_string = date_string[:-1]
        if len(date_string) > 0 and "-" in date_string[-1]:
            date_string = date_string[:-1]
    return date_string


def extract_relevant_data(data):
    """
    Extract relevant data from an OpenRefine data dictionary.

    Prioritises the original "value" over "match" (matched GND data)
    over "candidates" (potential GND matches).

    :param data: a dictionary with keys "value", "match", "candidates"
    :type data: dict
    :return: a string, dictionary or list of dictionaries containing data
             (or otherwise the empty string)
    :rtype: various
    """
    if data["value"]:
        return data["value"]
    elif data["match"]:
        return data["match"]
    elif data["candidates"]:
        return data["candidates"]
    return ""


class Command(BaseCommand):
    help = (
        "Import poster, performance, event data based on manually "
        "catalogued data enriched in OpenRefine."
    )

    def add_arguments(self, parser):
        parser.add_argument("--keep-history", action="store_true")
        parser.add_argument("--delete", action="extend", nargs="+", type=str)

    def handle(self, *args, **options):
        keep_history = options["keep_history"] or False

        if delete_args := options["delete"]:
            if "all" in delete_args:
                delete_models = get_relation_classes() + get_entity_classes() + [Uri]
                delete_objects(models=delete_models, keep_history=keep_history)
            else:
                if "relations" in delete_args:
                    delete_objects(
                        models=get_relation_classes(), keep_history=keep_history
                    )
                    delete_args.remove("relations")
                if "entities" in delete_args:
                    delete_objects(
                        models=get_entity_classes(), keep_history=keep_history
                    )
                    delete_args.remove("entities")
                if "uris" in delete_args:
                    delete_objects(models=[Uri], keep_history=keep_history)
                    delete_args.remove("uris")

                if delete_args:
                    delete_objects(models=delete_args, keep_history=keep_history)

            exit(0)

        # run mgmt command which ensures Thomas Bernhard instance exists
        call_command("create_tb")

        with open(OPENREFINE_EXPORT) as f:
            posters_raw_data = json.load(f)

            for row in posters_raw_data["rows"]:
                title = row["title"] or ""  # Poster, Event/Performance field "label"
                notes = row["notes"] or ""  # Poster field
                signature = row["signature"] or ""  # Poster field
                storage_location = row["storage_location"] or ""  # Poster field
                status = row["status"] or ""  # Poster field
                quantity = (
                    row["quantity"] or 0
                )  # Poster field – should never be zero, but raw data contains null values
                measurements = (
                    row["measurements"] or ""
                )  # Poster fields "height", "width"; should return empty
                country = row["country"] or ""  # Poster field
                year = row["year"] or ""  # Poster field
                event_type = (
                    row["event_type"] or ""
                )  # Event field if value not "Theater" (which denotes Performance)
                start_date_written = (
                    row["start_date_written"] or ""
                )  # Performance/Event field TODO use django-interval
                end_date_written = (
                    row["end_date_written"] or ""
                )  # Performance/Event field TODO use django-interval

                # data objects which may have GND IDs
                work_data = row["work"]  # Work entity
                director_data = row["director"]  # Person entity
                participants_array = row["participants"]  # Person entity
                group_data = row["group"]  # Group entity

                title = title.strip()
                notes = notes.strip()
                signature = signature.strip()
                storage_location = storage_location.strip()
                status = status.strip()
                if not isinstance(quantity, int):
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        notes = add_text(
                            notes,
                            f"Anzahl (konnte nicht konvertiert werden): {quantity}",
                        )
                        quantity = 0
                measurements = measurements.strip()
                country = country.strip()
                if isinstance(year, int):
                    year = str(year)
                else:
                    year = year.strip()
                event_type = event_type.strip()
                start_date_written = start_date_written.strip()
                end_date_written = end_date_written.strip()

                # add unexpected values and/or values from columns for which
                # there are no fields (yet) to Poster field "notes"
                if measurements:
                    notes = add_text(notes, f"Maße: {measurements}")

                if not event_type or event_type not in Event.EventTypes.values + [
                    "Theater"
                ]:
                    # record any data which would normally be linked with a
                    # Performance or Event object to Poster notes in case
                    # no such relation can be created
                    if not event_type:
                        notes = add_text(notes, "Plakat ohne Aufführung/Veranstaltung")
                    else:
                        notes = add_text(
                            notes,
                            f"Veranstaltungstyp unbekannt: {event_type}",
                        )
                    if start_date_written:
                        notes = add_text(notes, f"Datum Start: {start_date_written}")
                    if end_date_written:
                        notes = add_text(notes, f"Datum Ende: {end_date_written}")

                    if work_info := extract_relevant_data(work_data):
                        notes = add_text(notes, f"Werkbezug: {work_info}")
                    if director_info := extract_relevant_data(director_data):
                        notes = add_text(notes, f"Regisseur: {director_info}")
                    if group_info := extract_relevant_data(group_data):
                        notes = add_text(notes, f"Institution: {group_info}")
                    for p in participants_array:
                        if p_info := extract_relevant_data(p):
                            notes = add_text(notes, f"Beteiligte Personen: {p_info}")

                else:
                    # create date_range from dates without placeholders
                    # for posters with a valid event_type
                    # also log start and end date if year is not reflected
                    # in both to catch data inconsistencies
                    date_range = ""

                    start_date = convert_placeholder_dates(start_date_written)
                    end_date = convert_placeholder_dates(end_date_written)

                    if start_date:
                        date_range = f"ab {start_date}"
                        if year not in start_date:
                            notes = add_text(
                                notes, f"Datum Start: {start_date_written}"
                            )
                    if end_date:
                        date_range = f"{date_range} bis {end_date}"
                        if year not in start_date:
                            notes = add_text(notes, f"Datum Ende: {end_date_written}")

                logger.debug(f"[{posters_raw_data['rows'].index(row)}] {title}")

                poster, poster_created = Poster.objects.get_or_create(
                    country=country,
                    label=title,
                    notes=notes,
                    signature=signature,
                    status=status,
                    storage_location=storage_location,
                    quantity=quantity,
                    year=year,
                )

                # log issues with Poster data when creating new objects
                if poster_created:
                    if poster.label == "":
                        logger.warning(f"Poster ID {poster.id} has no title.")

                    if poster.quantity == 0:
                        logger.warning(
                            f'Poster "{poster.label}" (ID {poster.id}) has quantity 0.'
                        )

                if event_type:
                    participating_persons = []
                    participating_groups = []

                    for participant_data in participants_array:
                        # data was linked to GND data
                        if participant_data["match"]:
                            gnd_refs_objects = extract_gnd_refs(  # noqa
                                participant_data, exclude_types=["Work"]
                            )
                            for obj in gnd_refs_objects:
                                if "DifferentiatedPerson" in obj["types"]:
                                    person = PersonImporter(
                                        GND_URL + obj["id"], Person
                                    ).create_instance()
                                    if person:
                                        participating_persons.append(person)
                                if "CorporateBody" in obj["types"]:
                                    group = GroupImporter(
                                        GND_URL + obj["id"], Group
                                    ).create_instance()
                                    if group:
                                        participating_groups.append(group)
                        else:
                            # create participants from value;
                            # ATTN. may be multiple
                            if person_names := participant_data["value"]:
                                people = split_people(person_names)

                                for person in people:
                                    surname = person[0]
                                    forename = person[1]

                                    participant = Person.objects.filter(
                                        surname=surname,
                                        forename=forename,
                                    ).first()
                                    if not participant:
                                        participant = Person.objects.create(
                                            surname=surname,
                                            forename=forename,
                                        )

                                    participating_persons.append(participant)

                    # data was linked to GND data
                    if group_data["match"]:
                        gnd_refs_objects = extract_gnd_refs(  # noqa
                            group_data, exclude_types=["Work"]
                        )
                        for obj in gnd_refs_objects:
                            if "DifferentiatedPerson" in obj["types"]:
                                person = PersonImporter(
                                    GND_URL + obj["id"], Person
                                ).create_instance()
                                if person:
                                    participating_persons.append(person)
                            if "CorporateBody" in obj["types"]:
                                group = GroupImporter(
                                    GND_URL + obj["id"], Group
                                ).create_instance()
                                if group:
                                    participating_groups.append(group)

                    else:
                        # create group(s) from value; ATTN. may be multiple
                        if group_data["value"]:
                            group_labels = group_data["value"].split(";")

                            for label in group_labels:
                                label = label.strip()

                                group = Group.objects.filter(label=label).first()
                                if not group:
                                    group = Group.objects.create(label=label)

                                participating_groups.append(group)

                    if event_type == "Theater":
                        try:
                            # check if poster is already related to a performance
                            # before creating a new performance as there can only
                            # be one such relation per poster (and the data on
                            # performances is limited as long as we cannot save
                            # dates for them; like there can be multiple valid
                            # performances with the same label)
                            # TODO remove check once dates (and countries?)
                            #  are saved for performances
                            related_performance = PosterPromotedPerformance.objects.get(
                                subj_object_id=poster.pk,
                                subj_content_type=get_ct(Poster),
                                obj_content_type=get_ct(Performance),
                            )
                            performance = Performance.objects.get(
                                id=related_performance.obj_object_id
                            )
                        except ObjectDoesNotExist:
                            performance = Performance.objects.create(
                                label=title,
                                date_range=date_range,
                            )

                        PosterPromotedPerformance.objects.get_or_create(
                            subj_object_id=poster.pk,
                            obj_object_id=performance.pk,
                            subj_content_type=get_ct(Poster),
                            obj_content_type=get_ct(Performance),
                        )

                        # Performance can only be linked to one Work;
                        # data was linked to GND data
                        if work_data["match"]:
                            gnd_refs_objects = extract_gnd_refs(  # noqa
                                work_data,
                                exclude_types=["DifferentiatedPerson", "CorporateBody"],
                            )

                            for obj in gnd_refs_objects:
                                work = WorkImporter(
                                    GND_URL + obj["id"], Work
                                ).create_instance()
                        else:
                            # create work from value
                            if work_title := work_data["value"]:
                                work = Work.objects.filter(title=work_title).first()
                                if not work:
                                    work = Work.objects.create(title=work_title)

                        PerformancePerformedWork.objects.get_or_create(
                            subj_object_id=performance.pk,
                            obj_object_id=work.pk,
                            subj_content_type=get_ct(Performance),
                            obj_content_type=get_ct(Work),
                        )

                        directors_persons = []
                        directors_groups = []
                        # data was linked to GND data
                        # ATTN. directors may be persons or groups
                        if director_data["match"]:
                            gnd_refs_objects = extract_gnd_refs(  # noqa
                                director_data, exclude_types=["Work"]
                            )
                            for obj in gnd_refs_objects:
                                if "DifferentiatedPerson" in obj["types"]:
                                    person = PersonImporter(
                                        GND_URL + obj["id"], Person
                                    ).create_instance()
                                    if person:
                                        directors_persons.append(person)
                                if "CorporateBody" in obj["types"]:
                                    group = GroupImporter(
                                        GND_URL + obj["id"], Group
                                    ).create_instance()
                                    if group:
                                        directors_groups.append(group)
                        else:
                            # create director(s) from value;
                            # may be multiple people or groups, but we default
                            # to Person for manually catalogued data
                            if person_names := director_data["value"]:
                                people = split_people(person_names)

                                for person in people:
                                    surname = person[0]
                                    forename = person[1]

                                    director = Person.objects.filter(
                                        surname=surname,
                                        forename=forename,
                                    ).first()
                                    if not director:
                                        director = Person.objects.create(
                                            surname=surname,
                                            forename=forename,
                                        )

                                    directors_persons.append(director)

                        for director in directors_persons:
                            PerformanceHadDirectorPerson.objects.get_or_create(
                                subj_object_id=performance.pk,
                                obj_object_id=director.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Person),
                            )
                        for director in directors_groups:
                            logger.warning(
                                f'Performance "{performance.label}" (ID {performance.pk}) – missing relation PerformanceHadDirectorGroup for {director}.'
                            )
                            # TODO create new Relation PerformanceHadDirectorGroup
                            ...

                        if not directors_persons and not directors_groups:
                            logger.warning(
                                f'Performance "{performance.label}" (ID {performance.pk}) has no director.'
                            )

                        # create relationships between Performance and
                        # participating Persons and Groups
                        for person in participating_persons:
                            PerformanceHadParticipantPerson.objects.get_or_create(
                                subj_object_id=performance.pk,
                                obj_object_id=person.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Person),
                            )
                        for group in participating_groups:
                            PerformanceHadParticipantGroup.objects.get_or_create(
                                subj_object_id=performance.pk,
                                obj_object_id=group.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Group),
                            )

                    elif event_type in Event.EventTypes.values:
                        event = None
                        # Events can be about multiple works;
                        # data was linked to GND data
                        if work_data["match"]:
                            gnd_refs_objects = extract_gnd_refs(  # noqa
                                work_data,
                                exclude_types=["DifferentiatedPerson", "CorporateBody"],
                            )
                            work = WorkImporter(
                                GND_URL + gnd_refs_objects[0]["id"], Work
                            ).create_instance()

                        else:
                            # create work from value
                            if work_title := work_data["value"]:
                                work = Work.objects.filter(title=work_title).first()
                                if not work:
                                    work = Work.objects.create(title=work_title)

                        # a Poster may only be linked to a single Event, so check
                        # if there already is an Event linked to this Poster
                        # TODO remove this check once dates (and countries?)
                        #  are saved for Events
                        if poster_promos_event := PosterPromotedEvent.objects.filter(
                            subj_object_id=poster.pk,
                            subj_content_type=get_ct(Poster),
                            obj_content_type=get_ct(Event),
                        ).first():
                            event = Event.objects.get(
                                id=poster_promos_event.obj_object_id
                            )
                        if not event:
                            # check if there is an Event that matches without
                            # being connected to the Poster
                            if event := Event.objects.filter(
                                label=title,
                                event_type=event_type,
                                date_range__isnull=True,
                            ).first():
                                pass
                            # otherwise create a new Event
                            elif event := Event.objects.create(
                                label=title,
                                event_type=event_type,
                                date_range=date_range,
                            ):
                                pass

                            PosterPromotedEvent.objects.get_or_create(
                                subj_object_id=poster.pk,
                                obj_object_id=event.pk,
                                subj_content_type=get_ct(Poster),
                                obj_content_type=get_ct(Event),
                            )

                        # create relationships between Event and
                        # participating Persons and Groups
                        for person in participating_persons:
                            EventHadParticipantPerson.objects.get_or_create(
                                subj_object_id=event.pk,
                                obj_object_id=person.pk,
                                subj_content_type=get_ct(Event),
                                obj_content_type=get_ct(Person),
                            )
                        for group in participating_groups:
                            EventHadParticipantGroup.objects.get_or_create(
                                subj_object_id=event.pk,
                                obj_object_id=group.pk,
                                subj_content_type=get_ct(Event),
                                obj_content_type=get_ct(Group),
                            )
                    else:
                        if poster_created:
                            logger.warning(
                                f'No Event created – Poster "{poster.label}" (ID {poster.id}) promotes unknown event_type.'
                            )

                else:
                    if poster_created:
                        logger.warning(
                            f'No Event created – Poster "{poster.label}" (ID {poster.id}) has empty event_type.'
                        )
