import logging

import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from django.utils.translation import gettext_lazy as _

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
    and clicking through to each object's detail view.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            linkify=True,
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
    title = SortableLinkifyColumn()

    class Meta:
        fields = ["title", "subtitle"]
        order_by = "title"


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
    forename = tables.Column(
        verbose_name=_("Vorname"),
    )
    surname = tables.Column(
        verbose_name=_("Nachname"),
    )
    full_name = SortableLinkifyColumn(
        accessor="full_name",
        verbose_name=_("Name"),
        order_by=("surname", "forename"),
    )

    class Meta(BaseEntityTable.Meta):
        model = Person
        fields = ["full_name", "surname", "forename"]
        order_by = "surname"


class PlaceTable(BaseEntityTable):
    label = SortableLinkifyColumn(
        verbose_name=_("Name"),
    )

    class Meta(BaseEntityTable.Meta):
        model = Place
        fields = ["label"]
        order_by = "label"


class GroupTable(BaseEntityTable):
    label = SortableLinkifyColumn(
        verbose_name=_("Name"),
    )

    class Meta(BaseEntityTable.Meta):
        model = Group
        fields = ["label"]
        order_by = "label"


class EventTable(BaseEntityTable):
    label = SortableLinkifyColumn()

    class Meta(BaseEntityTable.Meta):
        model = Event
        fields = ["label"]
        order_by = "label"


class PerformanceTable(BaseEntityTable):
    label = SortableLinkifyColumn()

    class Meta(BaseEntityTable.Meta):
        model = Performance
        fields = ["label"]
        order_by = "label"


class PosterTable(BaseEntityTable):
    label = SortableLinkifyColumn()

    class Meta(BaseEntityTable.Meta):
        model = Poster
        fields = ["label"]
        order_by = "label"
