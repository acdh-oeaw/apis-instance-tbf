import logging

from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm

logger = logging.getLogger(__name__)


class WorkFilterSetForm(GenericFilterSetForm):
    columns_exclude = ["tbit_category"]


class WorkForm(GenericModelForm):
    class Meta(GenericModelForm.Meta):
        exclude = ["tbit_category"]
