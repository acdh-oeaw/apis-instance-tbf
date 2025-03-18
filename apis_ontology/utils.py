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
