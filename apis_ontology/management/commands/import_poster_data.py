import inspect
import json
import logging

from apis_core.apis_entities.utils import get_entity_classes
from apis_core.apis_metainfo.models import Uri
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from apis_ontology.importers import GroupImporter, PersonImporter, WorkImporter  # noqa
from apis_ontology.models import (  # noqa
    BaseRelation,
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
    PersonIsAuthorOfWork,
    Poster,
    PosterPromotedEvent,
    PosterPromotedPerformance,
    Work,
)

logger = logging.getLogger(__name__)

OPENREFINE_EXPORT = "data/posters/FTB_posters_initial_catalogue_refined.json"
GND_URL = "https://d-nb.info/gnd/"
GND_ID_TB = "118509861"  # GND ID for Thomas Bernhard


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


def get_ct(model):
    """
    Return the ContentType for a given model.
    """
    return ContentType.objects.get_for_model(model)


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
    Split raw data for multiple people.

    :param people:
    :type people:
    :return:
    :rtype:
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


def get_relation_classes():
    """
    Return all model classes which inherit from BaseRelation.

    :return: a list of model classes
    :rtype: list
    """
    return list(filter(lambda x: issubclass(x, BaseRelation), apps.get_models()))


def delete_objects(models=None, keep_history=False):
    """
    Delete model instance objects based on model classes and/or class names
    (i.e. string representations of the same).

    By default, all object histories are deleted alongside the objects
    themselves – the relevant history models are assumed to be named the
    same but prefixed with "Version" – unless keep_history
    is set to True.

    :param models: a list of model classes and/or class name strings
    :type models: list
    :param keep_history: whether to preserve object history or delete history
                         objects as well; defaults to deleting history
    :type keep_history: bool
    :return: a list of tuples whose first item is the total of deleted objects
             and whose second item is a dictionary with key-value pairs for
             every model class and deleted objects per class for every
             successful (non-zero) deletion, e.g.:
             (4, {'apis_ontology.Poster': 1,
             'apis_ontology.VersionPersonIsAuthorOfWork': 3})
    :rtype: list
    """
    deleted_objects = []
    for m in models:
        model_class = None

        if inspect.isclass(m):
            model_class = m
            model_name = m.__name__
        else:
            model_name = m
            try:
                model_class = apps.get_model("apis_ontology", model_name=model_name)
            except LookupError:
                pass

        if model_class:
            delete = model_class.objects.all().delete()
            if delete[0]:
                deleted_objects.append(delete)

        if not keep_history:
            historic_model_name = f"Version{model_name}"
            try:
                history_model_class = apps.get_model(
                    "apis_ontology", model_name=historic_model_name
                )
                delete = history_model_class.objects.all().delete()
                if delete[0]:
                    deleted_objects.append(delete)
            except LookupError:
                pass

    logger.debug("\n".join([str(d) for d in deleted_objects]))

    return deleted_objects


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

        # create Thomas Bernhard as first Person from GND ID
        PersonImporter(GND_URL + GND_ID_TB, Person).create_instance()

        with open(OPENREFINE_EXPORT) as f:
            posters_raw_data = json.load(f)
            # print(json.dumps(posters, sort_keys=True, indent=2))

            for row in posters_raw_data["rows"]:
                title = row["title"] or ""  # Poster, Event/Performance field "label"
                notes = row["notes"] or ""  # Poster field
                signature = row["signature"] or ""  # Poster field
                storage_location = row["storage_location"] or ""  # Poster field
                status = row["status"] or ""  # Poster field
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

                if not title:
                    logger.error(
                        f"There is no title for row {posters_raw_data['rows'].index(row)} "
                        f"(Work: {work_data['value']}, Director: {director_data['value']}, Group: {group_data['value']})"
                    )
                    title = "—"

                title = title.strip()
                notes = notes.strip()
                signature = signature.strip()
                storage_location = storage_location.strip()
                status = status.strip()
                measurements = measurements.strip()
                country = country.strip()
                if isinstance(year, int):
                    year = str(year)
                else:
                    year = year.strip()
                event_type = event_type.strip()
                start_date_written = start_date_written.strip()
                end_date_written = end_date_written.strip()

                # add unexpected values and values from columns for which
                # there are no fields (yet) to Poster field "notes";
                # relevant for:
                # signature, measurements, unknown event_types,
                # start_date_written, end_date_written TODO update
                if signature:
                    notes = add_text(notes, f"Signatur: {signature}")
                if measurements:
                    notes = add_text(notes, f"Maße: {measurements}")

                # add any dates to notes field while interval field is not
                # being used yet TODO replace with interval field
                if start_date_written:
                    notes = add_text(notes, f"Datum Start: {start_date_written}")
                if end_date_written:
                    notes = add_text(notes, f"Datum Ende: {end_date_written}")

                logger.debug(title)

                poster, created = Poster.objects.get_or_create(
                    country=country,
                    label=title,
                    notes=notes,
                    status=status,
                    storage_location=storage_location,
                    year=year,
                )
                poster_id = poster.pk

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
                            if participant_data["value"]:
                                people = split_people(participant_data["value"])

                                for person in people:
                                    participant, created = Person.objects.get_or_create(
                                        surname=person[0],
                                        forename=person[1],
                                    )
                                    if participant:
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
                            group_values = group_data["value"].split(";")

                            for val in group_values:
                                group, created = Group.objects.get_or_create(
                                    label=val,
                                )
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
                            performance = PosterPromotedPerformance.objects.get(
                                subj_object_id=poster_id,
                                subj_content_type=get_ct(Poster),
                                obj_content_type=get_ct(Performance),
                            )
                            performance_id = performance.obj_object_id
                        except ObjectDoesNotExist:
                            performance = Performance.objects.create(
                                label=title,
                            )
                            performance_id = performance.pk

                        PosterPromotedPerformance.objects.get_or_create(
                            subj_object_id=poster_id,
                            obj_object_id=performance_id,
                            subj_content_type=get_ct(Poster),
                            obj_content_type=get_ct(Performance),
                        )

                        # Performance can only be linked to one Work
                        # data was linked to GND data
                        if work_data["match"]:
                            gnd_refs_objects = extract_gnd_refs(  # noqa
                                work_data,
                                exclude_types=["DifferentiatedPerson", "CorporateBody"],
                            )

                            for obj in gnd_refs_objects:
                                work_import = WorkImporter(GND_URL + obj["id"], Work)
                                work = work_import.create_instance()

                                work_import_data = work_import.get_data(
                                    drop_unknown_fields=False
                                )
                                if "author" in work_import_data:
                                    author = PersonImporter(
                                        work_import_data["author"], Person
                                    ).create_instance()
                                    PersonIsAuthorOfWork.objects.get_or_create(
                                        subj_object_id=author.pk,
                                        obj_object_id=work.pk,
                                        subj_content_type=get_ct(Person),
                                        obj_content_type=get_ct(Work),
                                    )
                        else:
                            # create work from value
                            if work_data["value"]:
                                work, created = Work.objects.get_or_create(
                                    title=work_data["value"],
                                )

                        PerformancePerformedWork.objects.get_or_create(
                            subj_object_id=performance_id,
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
                            if director_data["value"]:
                                people = split_people(director_data["value"])

                                for person in people:
                                    director, created = Person.objects.get_or_create(
                                        surname=person[0],
                                        forename=person[1],
                                    )
                                    directors_persons.append(director)
                            else:
                                logger.warning(
                                    f"Performance {performance} (ID: {performance_id}) is missing director"
                                )

                        for director in directors_persons:
                            PerformanceHadDirectorPerson.objects.get_or_create(
                                subj_object_id=performance_id,
                                obj_object_id=director.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Person),
                            )
                        for director in directors_groups:
                            logger.warning(
                                f"Missing relation for director group: {director}"
                            )
                            # TODO create new Relation PerformanceHadDirectorGroup
                            ...

                        # create relationships between Performance and
                        # participating Persons and Groups
                        for person in participating_persons:
                            PerformanceHadParticipantPerson.objects.get_or_create(
                                subj_object_id=performance_id,
                                obj_object_id=person.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Person),
                            )
                        for group in participating_groups:
                            PerformanceHadParticipantGroup.objects.get_or_create(
                                subj_object_id=performance_id,
                                obj_object_id=group.pk,
                                subj_content_type=get_ct(Performance),
                                obj_content_type=get_ct(Group),
                            )

                    elif event_type in Event.EventTypes.values:
                        # Events can be about multiple works
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
                            if work_data["value"]:
                                work, created = Work.objects.get_or_create(
                                    title=work_data["value"],
                                )

                        try:
                            # a Poster may only be linked to one Event
                            # TODO remove this check once dates (and countries?)
                            #  are saved for performances
                            existing_poster_event = PosterPromotedEvent.objects.get(
                                subj_object_id=poster_id,
                                subj_content_type=get_ct(Poster),
                                obj_content_type=get_ct(Event),
                            )
                            event_id = existing_poster_event.obj_object_id
                        except ObjectDoesNotExist:
                            event, created = Event.objects.get_or_create(
                                label=title,
                                event_type=event_type,
                            )
                            event_id = event.pk

                        PosterPromotedEvent.objects.get_or_create(
                            subj_object_id=poster_id,
                            obj_object_id=event_id,
                            subj_content_type=get_ct(Poster),
                            obj_content_type=get_ct(Event),
                        )

                        # create relationships between Event and
                        # participating Persons and Groups
                        for person in participating_persons:
                            EventHadParticipantPerson.objects.get_or_create(
                                subj_object_id=event_id,
                                obj_object_id=person.pk,
                                subj_content_type=get_ct(Event),
                                obj_content_type=get_ct(Person),
                            )
                        for group in participating_groups:
                            EventHadParticipantGroup.objects.get_or_create(
                                subj_object_id=event_id,
                                obj_object_id=group.pk,
                                subj_content_type=get_ct(Event),
                                obj_content_type=get_ct(Group),
                            )
                    else:
                        # store unknown event types in notes
                        logger.warning(
                            f"Unknown event type for Poster {title} (ID {(poster_id)})"
                        )
                        notes = add_text(notes, f"Veranstaltungstyp: {event_type}")
                        Poster.objects.filter(id=poster_id).update(notes=notes)

                else:
                    logger.warning(
                        f"No event type for Poster {title} (ID {(poster_id)})"
                    )
