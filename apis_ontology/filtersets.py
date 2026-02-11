import logging

from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter

from apis_ontology.forms import BaseFilterSetForm, WorkFilterSetForm

logger = logging.getLogger(__name__)


class BaseEntityFilterSet(AbstractEntityFilterSet):
    """
    Parent FilterSet class for all entity classes.

    Applies settings to all entity list views (filter sidebars).
    """

    class Meta(AbstractEntityFilterSet.Meta):
        form = BaseFilterSetForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if choice_filters := self.get_choice_filters():
            for filter_name in choice_filters:
                self.reorder_choice_filter_choices(filter_name)

        if getattr(self.Meta, "model", False):
            if "search" in self.filters:
                s_filter = self.filters["search"]
                s_filter.label = _("Search across text fields")

                if (help_text := s_filter.extra.get("help_text")) and help_text.split(
                    ":"
                ):
                    fields_string = help_text.split(":")[1]
                    fields_list = fields_string.split(",")

                    # exclude Thomas Bernhard in translation-specific fields
                    # from combined search field
                    fields_list_filtered = ", ".join([
                        f
                        for f in fields_list
                        if ("in translation" not in f and "TBit" not in f)
                    ])

                    prefix = _("Searches in:")

                    s_filter.extra["help_text"] = format_lazy(
                        "{prefix} {fields}", prefix=prefix, fields=fields_list_filtered
                    )

    def get_choice_filters(self):
        """
        Get the names of all filters of type ChoiceFilter.

        :return: a list of strings representing the names of the filters
        :rtype: list
        """
        choice_filters = [
            name for name, f in self.base_filters.items() if type(f) is ChoiceFilter
        ]
        return choice_filters

    def reorder_choice_filter_choices(self, filter_name):
        """
        Reorder the choices in a ChoiceFilter by their (translated)
        labels.

        By default, choices in a ChoiceFilter are ordered by their values.
        This uses the human-readable labels, i.e. the display values, as basis
        for ordering the elements in the resulting dropdown.

        :param filter_name: the name of the filter to reorder
        :type filter_name: str
        """
        if filter_name in self.filters:
            f = self.filters[filter_name]
            if type(f) is ChoiceFilter:
                choices = f.extra.get("choices", [])
                sorted_choices = sorted(choices, key=lambda x: str(x[1]))
                f.extra["choices"] = sorted_choices


class WorkFilterSet(BaseEntityFilterSet):
    class Meta(BaseEntityFilterSet.Meta):
        exclude = ["tbit_category"]
        form = WorkFilterSetForm


class EventFilterSet(BaseEntityFilterSet):
    pass


class ManifestationFilterSet(BaseEntityFilterSet):
    class Meta(BaseEntityFilterSet.Meta):
        exclude = ["variety"]
