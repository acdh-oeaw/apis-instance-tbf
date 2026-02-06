import logging

from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

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
                    fields_list_filtered = ", ".join(
                        [
                            f
                            for f in fields_list
                            if ("in translation" not in f and "TBit" not in f)
                        ]
                    )

                    prefix = _("Searches in:")

                    s_filter.extra["help_text"] = format_lazy(
                        "{prefix} {fields}", prefix=prefix, fields=fields_list_filtered
                    )


class WorkFilterSet(BaseEntityFilterSet):
    class Meta(BaseEntityFilterSet.Meta):
        exclude = ["tbit_category"]
        form = WorkFilterSetForm
