import logging

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django_tables2.utils import A

from .models import (
    Event,
    Expression,
    Group,
    Item,
    Manifestation,
    Person,
    Place,
    Poster,
    Work,
)

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


class TitleFieldsMixin(tables.Table):
    class Meta:
        fields = ["title", "subtitle"]


class WorkTable(BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Work


class ExpressionTable(BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Expression


class ManifestationTable(BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Manifestation


class ItemTable(BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Item


class PersonTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Person
        fields = ["forename", "surname"]
        order_by = "surname"


class PlaceTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Place
        fields = ["label"]


class GroupTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Group
        fields = ["label"]


class EventTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Event
        fields = ["label"]


class PosterTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Poster
        fields = ["label"]
