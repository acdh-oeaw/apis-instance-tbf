import logging

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A

logger = logging.getLogger(__name__)


class SortableColumn(tables.Column):
    linkify = {
        "viewname": "apis_core:generic:detail",
        "args": [A("self_contenttype"), A("pk")],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            linkify=self.linkify,
            *args,
            **kwargs,
        )


class BaseEntityTable(AbstractEntityTable):
    """
    Base class for entity tables.
    """

    id = SortableColumn()

    class Meta(AbstractEntityTable.Meta):
        exclude = ["desc"]
        sequence = (
            "...",
            "id",
            "view",
            "edit",
            "delete",
            "noduplicate",
        )
