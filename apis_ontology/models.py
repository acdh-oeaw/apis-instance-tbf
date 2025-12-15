from apis_core.apis_entities.abc import E21_Person, E53_Place, E74_Group
from apis_core.apis_entities.models import AbstractEntity
from apis_core.history.models import VersionMixin
from apis_core.relations.models import Relation
from apis_core.utils.rdf import load_uri_using_path
from django.conf import settings
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
        max_length=1024,
        blank=True,
        default="",
        verbose_name=_("title"),
    )

    subtitle = models.CharField(
        max_length=1024,
        blank=True,
        default="",
        verbose_name=_("subtitle"),
    )

    # for additional/supplemental information provided in/with titles, e.g.
    # data stored in rdau:P60493 elements, issue/volume identifiers etc.
    other_title_information = models.CharField(
        max_length=1024,
        blank=True,
        default="",
        verbose_name=_("other title information"),
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

    class TBitCategories(models.TextChoices):
        """
        Categorisation of Works by Thomas Bernhard in translation website.

        TextChoices values are set to German short names since the working
        language is assumed to be German. Full names used by TBit are
        stored in (translatable) labels (partially modified to include
        super categories/labels as quasi prefix).
        """

        NOVELS = ("Romane", pgettext_lazy("TBit category", "prose: novels"))
        NOVELLAS = (
            "Novellen",
            pgettext_lazy("TBit category", "prose: novellas & short prose"),
        )
        AUTOBIOGRAPHY = (
            "Autobiografie",
            pgettext_lazy("TBit category", "prose: autobiography"),
        )
        DRAMA = "Drama", pgettext_lazy("TBit category", "drama & libretti")
        POETRY = "Lyrik", pgettext_lazy("TBit category", "poetry")
        OTHER = (
            "Sonstiges",
            pgettext_lazy(
                "TBit category",
                "other: letters, speeches, interviews & other writings",
            ),
        )
        ADAPTATIONS = (
            "Adaptionen",
            pgettext_lazy("TBit category", "adaptations"),
        )
        FRAGMENTS = "Fragmente", pgettext_lazy("TBit category", "fragments")

    tbit_category = models.CharField(
        max_length=1024,
        choices=TBitCategories.choices,
        blank=True,
        default="",
        verbose_name=_('"TB in translation" category'),
        help_text=_(
            'Used by "Thomas Bernhard in translation" to group works by '
            "genre and/or type."
        ),
    )

    class Meta(TitlesMixin.Meta):
        verbose_name = _("work")
        verbose_name_plural = _("works")

    import_definitions = {
        "https://d-nb.info/*|/.*.rdf": lambda x: load_uri_using_path(
            x, settings.RDF_CONFIG_ROOT / "WorkFromDNB.toml"
        ),
    }


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

    language = models.CharField(
        blank=True,
        default="",
        max_length=12,
        verbose_name=_("language"),
    )

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

    isbn = models.CharField(
        blank=True,
        default="",
        max_length=17,
        verbose_name="ISBN",
        help_text=_(
            "Use hyphens or spaces to separate the individual parts of the "
            "ISBN or enter it as one continuous sequence. Ex. 978-3-518-06505-1"
        ),
    )

    relevant_pages = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name=_("relevant pages"),
        help_text=_(
            "Use semicolons to separate multiple pages or page ranges "
            "from one another. Ex. 7; 31-42; 185-210"
        ),
    )

    publication_date = FuzzyDateParserField(
        null=True,
        blank=True,
        verbose_name=_("publication date"),
        help_text=_(
            "Can be a full or partial date and also accepts (partial) date "
            "ranges to cover uncertain or unclear dates. A full date may be "
            "entered in DD.MM.YYYY or YYYY-MM-DD format, a partial date can "
            "be a full year YYYY or may otherwise be formatted MM.YYYY or "
            "YYYY-MM. "
            "Date ranges need to entered with keywords 'ab' ('from') and 'bis' "
            "('to') to mark their (exact or approximate) start and end dates. "
            "Ex. 1989. Ex. 1971-05. Ex. ab 1990-03-26 bis 1990-03-27."
        ),
    )

    tbit_shelfmark = models.CharField(
        blank=True,
        default="",
        max_length=50,
        verbose_name=_("TBit shelfmark"),
        help_text=_('Shelfmark of "Thomas Bernhard in translation" publications'),
    )

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
        pass

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
        pass


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
        pass

    import_definitions = E74_Group.import_definitions
    import_definitions["https://d-nb.info/*|/.*.rdf"] = lambda x: load_uri_using_path(
        x, settings.RDF_CONFIG_ROOT / "GroupFromDNB.toml"
    )


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

    import_definitions = {
        "https://d-nb.info/*|/.*.rdf": lambda x: load_uri_using_path(
            x, settings.RDF_CONFIG_ROOT / "EventFromDNB.toml"
        ),
    }


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
        verbose_name=_("height"),
        help_text=_("unit: mm"),
    )

    width = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("width"),
        help_text=_("unit: mm"),
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


class ItemHasKeeperGroup(BaseRelation):
    """
    Item "has keeper" Group relation.

    Property which associates an Item with a Group which acts as the item's
    custodian. E.g. a physical copy of a book which is stored at a particular
    library.

    Based on CIDOC CRM property P50 has current keeper (is current keeper of):
    https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html#P50
    """

    subj_model = Item
    obj_model = Group

    @classmethod
    def name(cls) -> str:
        return "has keeper"

    @classmethod
    def reverse_name(cls) -> str:
        return "is keeper of"


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


class PersonIsTranslatorOfExpression(BaseRelation):
    """
    Person is translator of Expression relation.
    """

    subj_model = Person
    obj_model = Expression

    @classmethod
    def name(cls) -> str:
        return "is translator of"

    @classmethod
    def reverse_name(cls) -> str:
        return "has translator"


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
