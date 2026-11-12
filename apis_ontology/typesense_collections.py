from apis_typesense.collections import BaseCollection
from apis_typesense.fields import (
    EnumField,
    FixedStringField,
    FuzzyDateField,
    SameAsField,
    TypesenseField,
)
from apis_typesense.models import ModelField, ModelSerializer
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    Case,
    CharField,
    Exists,
    F,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Cast, Concat, ExtractYear, JSONObject

from apis_ontology.models import (
    Event,
    EventHadParticipantGroup,
    EventHadParticipantPerson,
    EventWasMotivatedByWork,
    Expression,
    Group,
    GroupIsPublisherOfManifestation,
    Manifestation,
    ManifestationEmbodiesExpression,
    Performance,
    PerformanceHadDirectorPerson,
    PerformanceHadParticipantGroup,
    PerformanceHadParticipantPerson,
    PerformancePerformedWork,
    Person,
    PersonIsAuthorOfWork,
    PersonIsTranslatorOfExpression,
    Poster,
    PosterPromotedEvent,
    PosterPromotedPerformance,
    Work,
    WorkIsRealisedInExpression,
)

author_of = PersonIsAuthorOfWork.objects.filter(
    obj_object_id=OuterRef("pk")
).values_list("subj_object_id", flat=True)

transl_of = PersonIsTranslatorOfExpression.objects.filter(
    obj_object_id=OuterRef("pk")
).values_list("subj_object_id", flat=True)

manifest = Manifestation.objects.filter(id=OuterRef("subj_object_id")).order_by(
    "publication_date"
)[:1]
exp_man = ManifestationEmbodiesExpression.objects.filter(
    obj_object_id=OuterRef("id")
).annotate(
    language=Subquery(manifest.values("primary_language")),
    year=Subquery(manifest.values("publication_date")),
)[:1]
work_expr = WorkIsRealisedInExpression.objects.filter(obj_object_id=OuterRef("id"))[:1]
exp_man_2 = ManifestationEmbodiesExpression.objects.filter(
    obj_object_id=OuterRef("id")
).values_list("subj_object_id", flat=True)

expressions = Expression.objects.all().annotate(
    work_id=Subquery(work_expr.values("subj_object_id")),
    transl=ArraySubquery(transl_of),
    language_man=Subquery(exp_man.values("language")),
    year=Subquery(exp_man.values("year")),
)
transl = expressions.exclude(transl__len=0)

persons = Person.objects.all().annotate(label=Concat("forename", Value(" "), "surname"))
persons_rel = Person.objects.filter(pk=OuterRef("obj_object_id")).annotate(
    label=Concat("forename", Value(" "), "surname")
)

perf_work = PerformancePerformedWork.objects.filter(subj_object_id=OuterRef("id"))[:1]
perf_direct = (
    PerformanceHadDirectorPerson.objects.filter(subj_object_id=OuterRef("id"))
    .annotate(
        aut_id=Subquery(persons_rel[:1].values("id")),
        aut_label=Subquery(persons_rel[:1].values("label")),
    )
    .values(json=JSONObject(id="aut_id", label="aut_label"))
)
perf_actor = (
    PerformanceHadParticipantPerson.objects.filter(subj_object_id=OuterRef("id"))
    .annotate(
        aut_id=Subquery(persons_rel[:1].values("id")),
        aut_label=Subquery(persons_rel[:1].values("label")),
    )
    .values(json=JSONObject(id="aut_id", label="aut_label"))
)
poster_perf = PosterPromotedEvent.objects.filter(obj_object_id=OuterRef("id"))
perf_group = PerformanceHadParticipantGroup.objects.filter(
    subj_object_id=OuterRef("id")
)
performance = Performance.objects.all().annotate(
    work_id=Subquery(perf_work.values("obj_object_id")),
    directors=ArraySubquery(perf_direct),
    actors=ArraySubquery(perf_actor),
    posters=ArraySubquery(poster_perf.values_list("subj_object_id", flat=True)),
    theaters=ArraySubquery(perf_group.values_list("obj_object_id", flat=True)),
)
man_work_year = WorkIsRealisedInExpression.objects.filter(
    subj_object_id=OuterRef("id")
).annotate(
    year=Subquery(
        ManifestationEmbodiesExpression.objects.filter(
            obj_object_id=OuterRef("obj_object_id")
        )
        .annotate(
            year=Subquery(manifest.values("publication_date")),
        )
        .order_by("year")
        .values("year")[:1]
    )
)
works = Work.objects.all().annotate(
    author=ArraySubquery(author_of), year=Subquery(man_work_year.values("year")[:1])
)
works_bernhard = works.filter(author__contains=[1])

manifest_publishers = GroupIsPublisherOfManifestation.objects.filter(
    obj_object_id=OuterRef("pk")
)

group_man = Group.objects.filter(id=OuterRef("subj_object_id"))[:1]

publications = Manifestation.objects.all().annotate(
    year=ExtractYear("publication_date_date_sort"),
    # only expressions with a translator are indexed in TranslationCollection
    translations=ArraySubquery(
        ManifestationEmbodiesExpression.objects.filter(
            Exists(
                PersonIsTranslatorOfExpression.objects.filter(
                    obj_object_id=OuterRef("obj_object_id")
                )
            ),
            subj_object_id=OuterRef("pk"),
        ).values_list("obj_object_id", flat=True)
    ),
    language=Case(
        When(language_variety="", then=F("primary_language")),
        default=Concat("primary_language", Value("_"), "language_variety"),
    ),
    publisher=Subquery(
        manifest_publishers.annotate(
            id_group=Cast("subj_object_id", CharField()),
            name_group=Subquery(group_man.values("label")),
        ).values(json=JSONObject(id="id_group", label="name_group"))[:1]
    ),
)

ev_group = EventHadParticipantGroup.objects.filter(subj_object_id=OuterRef("pk"))[:1]
ev_participant = (
    EventHadParticipantPerson.objects.filter(subj_object_id=OuterRef("pk"))
    .annotate(
        part_id=Subquery(persons_rel[:1].values("id")),
        part_label=Subquery(persons_rel[:1].values("label")),
    )
    .values(json=JSONObject(id="part_id", label="part_label"))
)
ev_work = EventWasMotivatedByWork.objects.filter(subj_object_id=OuterRef("pk"))[:1]
events = Event.objects.all().annotate(
    work_id=Subquery(ev_work.values("obj_object_id")),
    participants=ArraySubquery(ev_participant),
    location=Subquery(ev_group.values("obj_object_id")),
)
poster_work = (
    PosterPromotedPerformance.objects.filter(subj_object_id=OuterRef("pk"))
    .annotate(
        work_id=Subquery(
            PerformancePerformedWork.objects.filter(
                subj_object_id=OuterRef("obj_object_id")
            ).values("obj_object_id")[:1]
        )
    )
    .values("work_id")[:1]
)
poster_perf = PosterPromotedPerformance.objects.filter(
    subj_object_id=OuterRef("pk")
).values("obj_object_id")[:1]
posters = Poster.objects.all().annotate(
    work_id=Subquery(poster_work), performance_id=Subquery(poster_perf)
)


class EntityModel(ModelSerializer):
    id: TypesenseField = TypesenseField(type="string", field_name="id")
    name: TypesenseField = TypesenseField(type="string", field_name="label")


class WorkCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    category: TypesenseField = TypesenseField(
        type="string", field_name="tbit_category", optional=True, facet=True
    )
    year: TypesenseField = TypesenseField(
        type="int32", optional=True, field_name="year", sort=True, facet=True
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")

    default_models = [(works_bernhard, {"filter": {}, "exclude": {}})]
    collection_name = "work"
    default_sorting_field = "title"


class TranslationCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    language: EnumField = EnumField(
        source="index", type="string", field_name="language_man", facet=True
    )
    type: FixedStringField = FixedStringField(value="translation", type="string")
    translator_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="transl",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    year: TypesenseField = TypesenseField(
        type="int32", optional=True, field_name="year", sort=True, facet=True
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(transl, {"filter": {}, "exclude": {}})]
    collection_name = "translation"
    default_sorting_field = "title"


class PerformanceCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="label")
    type: FixedStringField = FixedStringField(value="performance", type="string")
    directors: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=EntityModel(),
        accessor="directors",
        facet=True,
    )
    actors: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=EntityModel(),
        accessor="actors",
        facet=True,
    )
    poster_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="posters",
        reference="tbo_poster.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    theater_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="theaters",
        reference="tbo_group.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )

    dates: FuzzyDateField = FuzzyDateField(field_name="date_range")
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(performance, {"filter": {}, "exclude": {}})]
    collection_name = "performance"
    default_sorting_field = "title"


class EventCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        optional=True,
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="label")
    type_of_event: EnumField = EnumField(
        source="index", type="string", sort=True, facet=True, field_name="event_type"
    )
    type: FixedStringField = FixedStringField(value="event", type="string")
    participant_ids: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=EntityModel(),
        accessor="participants",
        facet=True,
    )
    location_id: TypesenseField = TypesenseField(
        type="string",
        optional=True,
        field_name="location",
        reference="tbo_group.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )

    dates: FuzzyDateField = FuzzyDateField(field_name="date_range")
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(events, {"filter": {}, "exclude": {}})]
    collection_name = "event"
    default_sorting_field = "title"


class PosterCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="label")
    type: FixedStringField = FixedStringField(value="poster", type="string")
    performance_id: TypesenseField = TypesenseField(
        type="string",
        optional=True,
        field_name="performance_id",
        reference="tbo_performance.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    year: TypesenseField = TypesenseField(
        type="int32", field_name="year", optional=True, sort=True, facet=True
    )
    country: EnumField = EnumField(
        type="string",
        field_name="country",
        source="index",
        optional=True,
        facet=True,
        sort=True,
    )

    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(posters, {"filter": {}, "exclude": {}})]
    collection_name = "poster"
    default_sorting_field = "title"


class PublicationCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    title: TypesenseField = TypesenseField(type="string", field_name="title", sort=True)
    subtitle: TypesenseField = TypesenseField(
        type="string", field_name="subtitle", sort=True, optional=True
    )
    other_title_information: TypesenseField = TypesenseField(
        type="string", field_name="other_title_information", sort=True, optional=True
    )
    isbn: TypesenseField = TypesenseField(
        type="int32", field_name="isbn", sort=True, optional=True
    )
    relevant_pages: TypesenseField = TypesenseField(
        type="string", field_name="relevant_pages", sort=True, optional=True
    )
    tbit_shelfmark: TypesenseField = TypesenseField(
        type="string", field_name="relevant_pages", sort=True, optional=True
    )
    language: EnumField = EnumField(
        type="string", field_name="language", source="index", facet=True
    )
    publication_date: FuzzyDateField = FuzzyDateField(field_name="publication_date")
    year: TypesenseField = TypesenseField(
        type="int32", optional=True, field_name="year", sort=True, facet=True
    )
    translations: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="translations",
        reference="tbo_translation.id",
        async_reference=True,
        cascade_delete=False,
        facet=True,
    )
    source: EnumField = EnumField(
        type="string",
        values=["tbit", "privatbibliothek"],
        extractor=lambda obj: "tbit" if obj.translations else "privatbibliothek",
        facet=True,
    )
    publisher: ModelField = ModelField(
        type="object", optional=True, model=EntityModel(), accessor="publisher"
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(publications, {"filter": {}, "exclude": {}})]
    collection_name = "publication"
    default_sorting_field = "title"

    def get_schema(self):
        # apis_typesense does not emit nested sub-fields, so declare them here
        schema = super().get_schema()
        schema["fields"] += [
            TypesenseField(
                type="string",
                optional=True,
                reference="tbo_group.id",
                async_reference=True,
                cascade_delete=False,
            ).to_schema("publisher.id"),
            TypesenseField(type="string", optional=True).to_schema("publisher.name"),
        ]
        return schema


class PersonCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label", sort=True)
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(persons, {"filter": {}, "exclude": {}})]
    collection_name = "person"
    default_sorting_field = "name"


class GroupCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label", sort=True)
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(Group.objects.all(), {"filter": {}, "exclude": {}})]
    collection_name = "group"
    default_sorting_field = "name"
