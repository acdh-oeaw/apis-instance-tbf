from apis_core.apis_entities.abc import E21_Person, E53_Place, E74_Group
from apis_core.apis_entities.models import AbstractEntity
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_interval.fields import FuzzyDateParserField


class BaseEntity(VersionMixin, AbstractEntity):
    """
    Base class for all entities.
    """

    class Meta:
        abstract = True
        ordering = ["id"]


class BaseRelation(VersionMixin, Relation):
    """
    Base class for all relations.
    """

    subj_model = None
    obj_model = None

    class Meta:
        abstract = True
        ordering = ["id"]


class TitlesMixin(models.Model):
    """
    Mixin for fields shared between work-like entities.
    """

    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("title"),
    )

    subtitle = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("subtitle"),
    )

    class Meta:
        abstract = True
        ordering = ["title"]

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

    class Meta(TitlesMixin.Meta):
        verbose_name = _("work")
        verbose_name_plural = _("works")


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

    class Meta(TitlesMixin.Meta):
        verbose_name = _("expression")
        verbose_name_plural = _("expressions")


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

    class Meta(TitlesMixin.Meta):
        verbose_name = _("manifestation")
        verbose_name_plural = _("manifestations")


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

    class Meta(TitlesMixin.Meta):
        verbose_name = _("item")
        verbose_name_plural = _("items")


class Person(BaseEntity, E21_Person):
    """
    Real persons who live or are assumed to have lived.

    Based on CIDOC CRM class E21 Person:
    https://www.cidoc-crm.org/html/cidoc_crm_v7.1.3.html#E21
    """

    class Meta(E21_Person.Meta):
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return self.full_name()

    def full_name(self):
        """
        Combine a Person's forename and surname (where available) into
        their full name following the format "Forename Surname".

        :return: a Person's full name
        :rtype: str
        """
        full_name = ""
        surname = self.surname
        forename = self.forename

        if forename != "" and surname != "":
            full_name = f"{forename} {surname}"
        elif surname != "":
            full_name = surname
        elif forename != "":
            full_name = forename
        else:
            pass

        return full_name


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

    class Meta(E53_Place.Meta):
        verbose_name = _("place")
        verbose_name_plural = _("places")

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

    class Meta(E74_Group.Meta):
        verbose_name = _("group")
        verbose_name_plural = _("groups")

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

    class EventTypes(models.TextChoices):
        EXHIBITION = "Ausstellung", _("exhibition")
        BOOK_PRESENTATION = "Buchpräsentation", _("book presentation")
        CONFERENCE = "Konferenz", _("conference")
        BOOK_READING = "Lesung", _("book reading")
        SCREENING = "Videovorführung", _("screening")
        LECTURE = "Vortrag", _("lecture")

    label = models.CharField(
        blank=True,
        default="",
        max_length=4096,
        verbose_name=pgettext_lazy(
            "verbose_name for Event class field 'label'", "label"
        ),
    )

    event_type = models.CharField(
        max_length=1024,
        choices=EventTypes.choices,
        blank=True,
        default="",
        verbose_name=_("event type"),
    )

    date_range = FuzzyDateParserField(
        blank=True,
        default="",
        verbose_name=_("date range"),
        help_text=_(
            'Input has to be formatted "ab YYYY-MM-DD bis YYYY-MM-DD" for '
            "from and to date, though either date is optional and dates may "
            "also remain incomplete. Ex. ab 1982-02 bis 1982-03"
        ),
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["label"]

    def __str__(self):
        return self.label


class Performance(BaseEntity):
    """
    Activities presenting or communicating Works directly or indirectly
    to an audience.

    Performances include theatre plays, musical works, choreographic works etc.
    They are always associated with a single Work, but may consist of other
    Performances as parts (e.g. a piano concerto with multiple movements)
    or cover a complete run of equivalent performances of the same work.
    They may be based on specific Expressions (e,g. translations), be created
    according to specific staging directions or be influenced by or include
    elements of other works.

    Example: the performance of Verdi's "La Traviata" at the Salzburg Festival
    in 2005, staged by Willy Decker, directed by Brian Large and featuring
    Anna Netrebko and Rolando Villazón.

    Based on LRMoo property F31 Performance:
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#F31
    """

    label = models.CharField(
        blank=True,
        default="",
        max_length=4096,
        verbose_name=pgettext_lazy(
            "verbose_name for Performance class field 'label'", "label"
        ),
    )

    date_range = FuzzyDateParserField(
        blank=True,
        default="",
        verbose_name=_("date range"),
        help_text=_(
            'Input has to be formatted "ab YYYY-MM-DD bis YYYY-MM-DD" for '
            "from and to date, though either date is optional and dates may "
            "also remain incomplete. Ex. ab 1982-02 bis 1982-03"
        ),
    )

    class Meta:
        verbose_name = _("performance")
        verbose_name_plural = _("performances")
        ordering = ["label"]

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
        verbose_name=pgettext_lazy(
            "verbose_name for Poster class field 'label'", "label"
        ),
    )

    signature = models.CharField(
        blank=True,
        default="",
        max_length=20,
        verbose_name=_("signature"),
    )

    storage_location = models.CharField(
        blank=True,
        default="",
        max_length=1024,
        verbose_name=_("storage location"),
    )

    status = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name=_("status"),
    )

    country = models.CharField(
        blank=True,
        default="",
        max_length=2,
        verbose_name=_("country"),
    )

    year = models.CharField(
        blank=True,
        default="",
        max_length=4,
        verbose_name=_("year"),
    )

    notes = models.TextField(
        blank=True,
        default="",
        max_length=1024,
        verbose_name=_("notes"),
    )

    height = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("length"),
    )

    width = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("width"),
    )

    quantity = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("quantity"),
    )

    class Meta:
        verbose_name = _("poster")
        verbose_name_plural = _("posters")
        ordering = ["label"]

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


class EventWasMotivatedByWork(BaseRelation):
    """
    Event was motivated by Work relation.

    Describes Works regarded as reason for carrying out an Event.

    Based on CIDOC CRM property P17 was motivated by (motivated):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P17
    """

    subj_model = Event
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "was motivated by"

    @classmethod
    def reverse_name(cls) -> str:
        return "motivated"


class EventHadParticipantPerson(BaseRelation):
    """
    Event had (not further specified) participant Person relation.

    Based on CIDOC CRM property P11 had participant (participated in):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P11
    """

    subj_model = Event
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "had participant"

    @classmethod
    def reverse_name(cls) -> str:
        return "participated in"


class EventHadParticipantGroup(BaseRelation):
    """
    Event had (not further specified) participant Group relation.

    Group could be the host, an organizer, advertiser,...

    Based on CIDOC CRM property P11 had participant (participated in):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P11
    """

    subj_model = Event
    obj_model = Group

    @classmethod
    def name(cls) -> str:
        return "had participant"

    @classmethod
    def reverse_name(cls) -> str:
        return "participated in"


class PerformancePerformedWork(BaseRelation):
    """
    Performance performed Work relation.

    Based on LRMoo property R80 performed (is performed in):
    https://cidoc-crm.org//extensions/lrmoo/html/LRMoo_v1.0.html#R80
    """

    subj_model = Performance
    obj_model = Work

    @classmethod
    def name(cls) -> str:
        return "performed"

    @classmethod
    def reverse_name(cls) -> str:
        return "is performed in"


class PerformanceHadDirectorPerson(BaseRelation):
    """
    Performance had director Person relation.

    Modelled after CIDOC CRM property P11 had participant.
    """

    subj_model = Performance
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "had director"

    @classmethod
    def reverse_name(cls) -> str:
        return "directed"


class PerformanceHadParticipantPerson(BaseRelation):
    """
    Performance had (not further specified) participant Person relation.

    Based on CIDOC CRM property P11 had participant (participated in):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P11
    """

    subj_model = Performance
    obj_model = Person

    @classmethod
    def name(cls) -> str:
        return "had participant"

    @classmethod
    def reverse_name(cls) -> str:
        return "participated in"


class PerformanceHadParticipantGroup(BaseRelation):
    """
    Performance had (not further specified) participant Group relation.

    Group could be the host, an organizer, advertiser,...

    Based on CIDOC CRM property P11 had participant (participated in):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P11
    """

    subj_model = Performance
    obj_model = Group

    @classmethod
    def name(cls) -> str:
        return "had participant"

    @classmethod
    def reverse_name(cls) -> str:
        return "participated in"


class PosterPromotedEvent(BaseRelation):
    """
    Poster promoted (advertised, announced,...) Event relation.
    """

    subj_model = Poster
    obj_model = Event

    @classmethod
    def name(cls) -> str:
        return "promoted"

    @classmethod
    def reverse_name(cls) -> str:
        return "was promoted by"


class PosterPromotedPerformance(BaseRelation):
    """
    Poster promoted (advertised, announced,...) Performance relation.
    """

    subj_model = Poster
    obj_model = Performance

    @classmethod
    def name(cls) -> str:
        return "promoted"

    @classmethod
    def reverse_name(cls) -> str:
        return "was promoted by"
