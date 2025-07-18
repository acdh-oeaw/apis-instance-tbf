import logging

from apis_core.apis_entities.filtersets import AbstractEntityFilterSet

from apis_ontology.forms import WorkFilterSetForm

logger = logging.getLogger(__name__)


class BaseEntityFilterSet(AbstractEntityFilterSet):
    pass


class WorkFilterSet(BaseEntityFilterSet):
    class Meta(BaseEntityFilterSet.Meta):
        exclude = ["tbit_category"]
        form = WorkFilterSetForm
