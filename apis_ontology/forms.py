import logging

from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm

logger = logging.getLogger(__name__)


class BaseFilterSetForm(GenericFilterSetForm):
    """
    Base form for FilterSets. Used in filter sidebars.
    """

    pass


class WorkFilterSetForm(BaseFilterSetForm):
    columns_exclude = ["tbit_category"]


class WorkForm(GenericModelForm):
    class Meta(GenericModelForm.Meta):
        exclude = ["tbit_category"]
