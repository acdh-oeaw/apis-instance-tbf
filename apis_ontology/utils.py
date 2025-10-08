"""
Utility/helper functions.
"""

import inspect
import logging

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
    :param dry_run: use to simulate object deletion; allows to check which
                    objects will be deleted with the given arguments before
                    actually deleting them
    :type dry_run: bool
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
