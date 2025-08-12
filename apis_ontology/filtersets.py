import logging

from apis_core.apis_entities.filtersets import AbstractEntityFilterSet

from apis_ontology.forms import WorkFilterSetForm

logger = logging.getLogger(__name__)


class BaseEntityFilterSet(AbstractEntityFilterSet):
    """
    Parent FilterSet class for all entity classes.

    Applies settings to all entity list views (filter sidebars).
    """

    pass


class WorkFilterSet(BaseEntityFilterSet):
    class Meta(BaseEntityFilterSet.Meta):
        exclude = ["tbit_category"]
        form = WorkFilterSetForm
