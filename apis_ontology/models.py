from apis_core.apis_entities.abc import E21_Person, E53_Place, E74_Group
from apis_core.apis_entities.models import AbstractEntity
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseEntity(VersionMixin, AbstractEntity):
    """
    Base class for all entities.
    """

    class Meta:
        abstract = True


class BaseRelation(VersionMixin, Relation):
    """
    Base class for all relations.
    """

    subj_model = None
    obj_model = None

    class Meta:
        abstract = True


class TitlesMixin(models.Model):
    """
    Mixin for fields shared between work-like entities.
    """

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Titel"),
    )

    subtitle = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Untertitel"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Work(TitlesMixin, BaseEntity):
    """
    Distinct intellectual ideas conveyed in artistic and intellectual
    creations.

    A Work is the outcome of an intellectual process of one or more persons.
    It exists in a recognisable realisations the form of one or more
    Expressions (whether finished or partial).
    Examples: Agatha Christie’s "Murder on the Orient Express" [novel],
    Alfred Hitchcock's "Psycho" [movie], John Lennon and Paul McCartney's
    "I want to hold your hand" [song].

    Based on LRMoo class F1 Work:
    https://www.cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.0.html#F1
    """

    class Meta:
        verbose_name = _("Werk")
        verbose_name_plural = _("Werke")


class Expression(TitlesMixin, BaseEntity):
    """
    Intellectual or artistic realisations of Works in the form of identifiable
    immaterial objects.

    Expressions can be texts, poems, jokes, musical notations, images,
    multimedia objects etc. as well as combinations of such objects.
    Examples: the original English text by Agatha Christie for her novel
    "Murder on the Orient Express"; the German text of "Murder on the Orient
    Express" as translated by Elisabeth van Bebber and published with the
    title "Mord im Orientexpress".

    Based on LRMoo class F2 Expression:
    https://www.cidoc-crm.org/extensions/lrmoo/html/LRMoo_v1.0.html#F2
    """

    class Meta:
        verbose_name = _("Expression")
        verbose_name_plural = _("Expressionen")


class Manifestation(TitlesMixin, BaseEntity):
    """
    Products rendering one or more Expressions.

    Often the outcome of a publication process during which Expressions are
    prepared for public dissemination (with Manifestations typically
    incorporating one or more Expressions). Different publishing formats,
    e.g. hard-cover vs. paperback editions, equal distinct instances
    of Manifestations.
    Example: the publication "Murder on the Orient Express / Agatha Christie",
    published by Collins Crime Club in 1934.

    Based on LRMoo class F3 Manifestation:
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#F3
    """

    class Meta:
        verbose_name = _("Manifestation")
        verbose_name_plural = _("Manifestationen")


class Item(TitlesMixin, BaseEntity):
    """
    Physical objects which were produced by an industrial process
    involving a specific Manifestation.

    Items include printed books, sheet music, CDs, DVDs etc.
    All instances of an Item associated with a particular Manifestation
    are expected to be identical (leaving aside any defects resulting from
    accidents during the production process or subsequent alterations
    or degradations).
    Example: the bronze statue of Auguste Rodin's "The Thinker", cast at the
    Fonderie Alexis Rudier in 1904, held at the Musée Rodin in Paris, France,
    since 1922.

    Based on LRMoo class F5 Item:
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#F5
    """

    class Meta:
        verbose_name = _("Exemplar")
        verbose_name_plural = _("Exemplare")


class Person(BaseEntity, E21_Person):
    """
    Real persons who live or are assumed to have lived.

    Based on CIDOC CRM class E21 Person:
    https://www.cidoc-crm.org/html/cidoc_crm_v7.1.3.html#E21
    """

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Personen")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("forename").verbose_name = "Vorname"
        self._meta.get_field("surname").verbose_name = "Nachname"
        self._meta.get_field("gender").verbose_name = "Geschlecht"
        self._meta.get_field("date_of_birth").verbose_name = "Geburtsdatum"
        self._meta.get_field("date_of_death").verbose_name = "Sterbedatum"

    def __str__(self):
        return f"{self.forename} {self.surname}"


class Place(BaseEntity, E53_Place):
    """
    Extents in the natural space where people live, in particular
    on the surface of the Earth.

    Usually determined by reference to the position of "immobile" objects
    such as buildings, cities, mountains, rivers etc. or identifiable by
    global coordinates or absolute reference systems.

    Based on CIDOC CRM class E53 Place:
    https://www.cidoc-crm.org/html/cidoc_crm_v7.1.3.html#E53
    """

    class Meta:
        verbose_name = _("Ort")
        verbose_name_plural = _("Orte")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("label").verbose_name = "Name"
        self._meta.get_field("latitude").verbose_name = "Latitüde"
        self._meta.get_field("longitude").verbose_name = "Longitüde"

    def __str__(self):
        return self.label


class Group(BaseEntity, E74_Group):
    """
    Any gatherings or organizations of human individuals or groups that act
    collectively or in a similar way.

    A gathering of people becomes an instance of Group when it exhibits
    organisational characteristics (e.g. ideas or beliefs held in common, or
    actions performed together).

    Based on CIDOC CRM class E74 Group:
    https://www.cidoc-crm.org/html/cidoc_crm_v7.1.3.html#E74
    """

    class Meta:
        verbose_name = _("Körperschaft")
        verbose_name_plural = _("Körperschaften")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field("label").verbose_name = "Name"

    def __str__(self):
        return self.label


class Event(BaseEntity):
    """
    Processes and interactions of a material nature, in cultural, social or
    physical systems.

    Typical examples are meetings, births, deaths, actions of decision taking,
    making or inventing things, but also more complex and extended ones
    such as conferences, elections, building of a castle, or battles.

    Based on CIDOC CRM class E5 Event:
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#E5
    """

    label = models.CharField(
        blank=True,
        default="",
        max_length=4096,
        verbose_name=_("Titel"),
    )

    class Meta:
        verbose_name = _("Veranstaltung")
        verbose_name_plural = _("Veranstaltungen")

    def __str__(self):
        return self.label


class Poster(BaseEntity):
    """
    A physical object conveying information about an Event.

    Typically used for a print product affixed to a vertical surface
    which advertises an upcoming event which may be of interest to
    viewers/readers/the public.
    """

    label = models.CharField(
        blank=True,
        default="",
        max_length=4096,
        verbose_name=_("Titel"),
    )

    class Meta:
        verbose_name = _("Plakat")
        verbose_name_plural = _("Plakate")

    def __str__(self):
        return self.label


class WorkIsRealisedInExpression(BaseRelation):
    """
    Work is realised in Expression.

    Property for the association between a Work and an Expression which
    conveys the Work.
    E.g. Agatha Christie's work "Murder on the Orient Express" is realised
    in the original text written by the author for the novel. The same work
    is also realised in the German translation by Elisabeth van Bebber as well
    as the narration of the English text by David Suchet.

    Based on LRMoo property R3 is realised in (realises):
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#R3
    """

    subj_model = Work
    obj_model = Expression

    @classmethod
    def name(cls) -> str:
        return "is realised in"

    @classmethod
    def reverse_name(cls) -> str:
        return "realises"


class ManifestationEmbodiesExpression(BaseRelation):
    """
    Manifestation embodies Expression.

    Property which associates a Manifestation with one or more Expressions
    which are rendered by the Manifestation.
    E.g. a novel N published by publisher P in year YYYY embodies the
    original text by author A. The German translation of the same novel, ND,
    published by publisher PD in a different year embodies the German
    translation by translator T.

    Based on LRMoo property R4 embodies (is embodied in):
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#R4
    """

    subj_model = Manifestation
    obj_model = Expression

    @classmethod
    def name(cls) -> str:
        return "embodies"

    @classmethod
    def reverse_name(cls) -> str:
        return "is embodied in"


class ItemExemplifiesManifestation(BaseRelation):
    """
    Item exemplifies Manifestation relation.

    Property which associate a Manifestation with an Item which is its
    exemplar.
    E.g. a particular book in a library with an inventory number
    exemplifies a certain publication (Manifestation) of a written work.

    Based on LRMoo property R7 exemplifies (is exemplified by):
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#R7
    """

    subj_model = Item
    obj_model = Manifestation

    @classmethod
    def name(cls) -> str:
        return "exemplifies"

    @classmethod
    def reverse_name(cls) -> str:
        return "is exemplified by"


class PersonIsAuthorOfWork(BaseRelation):
    """
    Person is author of Work relation.
    """

    subj_model = Person
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "is author of"

    @classmethod
    def reverse_name(cls) -> str:
        return "has author"


class GroupIsPublisherOfManifestation(BaseRelation):
    """
    Group is publisher of Manifestation relation.
    """

    subj_model = Group
    obj_model = Manifestation

    @classmethod
    def name(cls) -> str:
        return "is publisher of"

    @classmethod
    def reverse_name(cls) -> str:
        return "has publisher"
