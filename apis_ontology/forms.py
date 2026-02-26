import logging

from apis_core.generic.forms import GenericFilterSetForm, GenericModelForm
from django.forms import (
    ChoiceField,
    MultipleChoiceField,
    TypedChoiceField,
    TypedMultipleChoiceField,
)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if choice_fields := self.get_choice_fields():
            for field_name in choice_fields:
                self.fields[field_name].choices = sorted(
                    self.fields[field_name].choices, key=lambda x: x[1]
                )

    def get_choice_fields(self):
        """
        Get the names of all fields of type ChoiceField.

        :return: a list of strings representing the names of the fields
        :rtype: list
        """
        choice_fields = [
            name
            for name, f in self.fields.items()
            if type(f)
            in (
                ChoiceField,
                MultipleChoiceField,
                TypedChoiceField,
                TypedMultipleChoiceField,
            )
        ]
        return choice_fields


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
