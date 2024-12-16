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
    Performance,
    Person,
    Place,
    Poster,
    Work,
)

logger = logging.getLogger(__name__)


class SortableLinkifyColumn(tables.Column):
    """
    Custom table column which allows sorting of objects
    in ascending/descending order and which turns the string
    identifier for each individual object into a clickable
    link to its detail view.
    """

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

    id = SortableLinkifyColumn()

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


class WorkTable(TitleFieldsMixin, BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Work


class ExpressionTable(TitleFieldsMixin, BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Expression


class ManifestationTable(TitleFieldsMixin, BaseEntityTable):
    class Meta(TitleFieldsMixin.Meta, BaseEntityTable.Meta):
        model = Manifestation


class ItemTable(TitleFieldsMixin, BaseEntityTable):
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


class PerformanceTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Performance
        fields = ["label"]


class PosterTable(BaseEntityTable):
    class Meta(BaseEntityTable.Meta):
        model = Poster
        fields = ["label"]
