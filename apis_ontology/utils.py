"""
Utility/helper functions.
"""

import inspect
import logging

from apis_core.apis_entities.utils import get_entity_classes
from apis_core.apis_metainfo.models import RootObject
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from apis_ontology.models import BaseRelation

logger = logging.getLogger(__name__)


def get_ct(model):
    """
    Return the ContentType for a given model.
    """
    return ContentType.objects.get_for_model(model)


def get_relation_classes():
    """
    Return all model classes which inherit from BaseRelation.

    :return: a list of model classes
    :rtype: list
    """
    return list(filter(lambda x: issubclass(x, BaseRelation), apps.get_models()))


def get_history_model(model_name, name_prefix="Version"):
    """
    Look up the history model (class) for an existing model based on
    that model's name.

    :param model_name: name of a model for which to check if a history model
                       exists
    :type model_name: str
    :param name_prefix: can be used to provide a different name (prefix) for
                        model classes to be looked up; defaults to "Version"
    :type name_prefix: str
    :return: the history model class for the given model (if it exists)
    :rtype: class
    """
    history_model_class = None

    if not isinstance(model_name, str) or not isinstance(name_prefix, str):
        return None

    # do not look up history models for models which appear to be history models themselves
    if model_name.startswith(name_prefix):
        logger.warning(
            f"Aborting lookup of history model class for {model_name} "
            f"as it appears to be a history model itself."
        )
        return None

    if historic_model_name := f"{name_prefix}{model_name}":
        try:
            history_model_class = apps.get_model(
                "apis_ontology", model_name=historic_model_name
            )
        except LookupError as e:
            logger.warning(e)

    return history_model_class


def delete_objects(
    models=None,
    with_fields=None,
    with_values=None,
    operators=None,
    keep_history=False,
    dry_run=False,
):
    """
    Delete model instance objects based on model classes and/or class names
    (i.e. string representations of the same).

    By default, all object histories are deleted alongside the objects
    themselves – the relevant history models are assumed to be named the
    same but prefixed with "Version" – unless keep_history
    is set to True.

    :param models: a list of model classes and/or class names (strings)
    :type models: list
    :param with_fields: a list of model field names (strings)
    :type with_fields: list
    :param with_values: a list of values to look up for the given fields;
                        only works in conjunction with "with_fields" argument,
                        used for "params" argument with fields used in "where"
                        clause argument
    :type with_values: list
    :param operators: a list of comparison operators (strings) to use with
                       field names in "where" argument when lookup values are
                       provided via "params"; only works in conjunction with
                       "with_values", overrides "=" (equal) comparison as the
                       default comparison in "where" argument
    :type operators: list
    :param keep_history: whether to preserve object histories or to delete them
                         alongside the objects themselves; defaults to False,
                         i.e. deletes historical data as well
    :type keep_history: bool
    :return: a list of tuples whose first item is the total of deleted objects
             and whose second item is a dictionary with key-value pairs for
             every model class and deleted objects per class for every
             successful (non-zero) deletion, e.g.:
             (4, {'apis_ontology.Poster': 1,
             'apis_ontology.VersionPersonIsAuthorOfWork': 3})
    :rtype: list
    """
    history_model_class = None
    valid_model_classes = []

    objects = RootObject.objects.none()
    deleted_objects = []

    if with_values and not operators:
        operators = ["="]

    def construct_where_clause(fields, values, comp):
        where_clause = []
        params = []

        if not values:
            values = []

        # values need to be paired/pairable with fields
        if values:
            while len(comp) < len(values):
                comp.append(comp[-1])

            for f, c, v in zip(fields, comp, values):
                where_clause.append(f"{f} {c} %s")
                params.append(v)

        if (remaining_comp := comp[len(values) :]) and (
            remaining_fields := fields[len(values) :]
        ):
            for f, c in zip(remaining_fields, remaining_comp):
                where_clause.append(f"{f} {c}")

        return where_clause, params

    def delete_queryset(queryset, dry_run=False):
        deleted = queryset

        if not dry_run:
            if deleted_data := queryset.delete():
                if deleted_data[0]:
                    deleted = deleted_data

        return deleted

    if models:
        for m in models:
            class_name = None
            if inspect.isclass(m):
                class_name = m.__name__
            elif isinstance(m, str):
                class_name = m
            else:
                logger.debug(f"'Model' {m} is neither a class nor a string.")

            if class_name:
                try:
                    model_class = apps.get_model("apis_ontology", model_name=class_name)
                    valid_model_classes.append(model_class)
                except LookupError as e:
                    logger.warning(e)

        for model_class in valid_model_classes:
            model_name = model_class.__name__

            # only look up history models for models which aren't history models themselves
            if keep_history is False and not model_name.startswith("Version"):
                history_model_class = get_history_model(model_name)

            if with_fields:
                model_fields = [field.name for field in model_class._meta.get_fields()]

                if set(with_fields).issubset(set(model_fields)):
                    if not with_values and not operators:
                        objects = model_class.objects.all()
                        logger.debug(f"Deleting ALL {model_name} objects.")
                    else:
                        where_clause, params = construct_where_clause(
                            with_fields, with_values, operators
                        )
                        objects = model_class.objects.extra(
                            where=where_clause, params=params
                        )
                else:
                    logger.warning(
                        f"Unknown model field{'s' if len(with_fields) > 1 else ''} for "
                        f"{model_name} class: {', '.join(with_fields)}"
                    )

            else:
                objects = model_class.objects.all()

            if deleted := delete_queryset(objects, dry_run=dry_run):
                deleted_objects.append(deleted)
                if history_model_class:
                    object_ids = [o.pk for o in objects]
                    history_field_names = [
                        field.name for field in history_model_class._meta.get_fields()
                    ]
                    deleted_history = []

                    # history class for entity model
                    if "rootobject_ptr" in history_field_names:
                        deleted_history = delete_queryset(
                            history_model_class.objects.filter(
                                rootobject_ptr__in=object_ids
                            ),
                            dry_run=dry_run,
                        )
                    # history class for relation model
                    elif "relation_ptr" in history_field_names:
                        deleted_history = delete_queryset(
                            history_model_class.objects.filter(
                                relation_ptr__in=object_ids
                            ),
                            dry_run=dry_run,
                        )
                    if deleted_history:
                        deleted_objects.append(deleted_history)

    # if no models are provided but fields are, look through all (non-history) (entity) models for
    # ANY of the fields
    elif with_fields:
        for model_class in get_entity_classes():
            model_name = model_class.__name__

            if not model_name.startswith("Version"):
                if valid_fields := list(
                    set(with_fields).intersection(
                        [field.name for field in model_class._meta.get_fields()]
                    )
                ):
                    if keep_history is False:
                        history_model_class = get_history_model(model_name)

                    if not with_values and not operators:
                        logger.debug(f"Deleting ALL {model_name} objects.")
                        objects = model_class.objects.all()
                    else:
                        where_clause, params = construct_where_clause(
                            valid_fields, with_values, operators
                        )

                        where_clause = [" OR ".join(where_clause)]
                        objects = model_class.objects.extra(
                            where=where_clause, params=params
                        )

                    if deleted := delete_queryset(objects, dry_run=dry_run):
                        deleted_objects.append(deleted)
                        if history_model_class:
                            object_ids = [o.pk for o in objects]
                            if deleted_history := delete_queryset(
                                history_model_class.objects.filter(
                                    rootobject_ptr__in=object_ids
                                ),
                                dry_run=dry_run,
                            ):
                                deleted_objects.append(deleted_history)

    else:
        logger.warning("Nothing to delete – no models or fields provided.")

    return deleted_objects
