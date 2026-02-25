import logging

from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm

logger = logging.getLogger(__name__)


class BaseFilterSetForm(GenericFilterSetForm):
    """
    Base form for FilterSets. Used in filter sidebars.
    """

    pass


class BaseModelForm(GenericModelForm):
    """
    Base form for models. Used in create/edit views.
    """

    pass


class WorkFilterSetForm(BaseFilterSetForm):
    columns_exclude = ["tbit_category"]


class WorkForm(BaseModelForm):
    class Meta(GenericModelForm.Meta):
        exclude = ["tbit_category"]


class ManifestationForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["tbit_shelfmark"].disabled = True

            if self.instance.tbit_shelfmark != "":
                # disable language fields only for Manifestations imported from
                # TBit publications, to prevent (accidental) data manipulation
                self.fields["primary_language"].disabled = True
                self.fields["variety"].disabled = True
