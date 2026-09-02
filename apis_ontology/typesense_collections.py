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
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat, JSONObject

from apis_ontology.models import (
    Expression,
    Group,
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

expressions = Expression.objects.all().annotate(
    work_id=Subquery(work_expr.values("subj_object_id")),
    transl=ArraySubquery(transl_of),
    language_man=Subquery(exp_man.values("language")),
    year=Subquery(exp_man.values("year")),
)

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


class PersonModel(ModelSerializer):
    id: TypesenseField = TypesenseField(type="string", field_name="id")
    name: TypesenseField = TypesenseField(type="string", field_name="label")


class WorkCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    category: TypesenseField = TypesenseField(
        type="string", field_name="tbit_category", optional=True, facet=True
    )
    author_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="author",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
    )
    year: TypesenseField = TypesenseField(
        type="int32", optional=True, field_name="year", sort=True, facet=True
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")

    default_models = [(works, {"filter": {}, "exclude": {}})]
    collection_name = "work"
    default_sorting_field = "title"


class ExpressionCollection(BaseCollection):
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
    type: FixedStringField = FixedStringField(value="expression", type="string")
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
    default_models = [(expressions, {"filter": {}, "exclude": {}})]
    collection_name = "expression"
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
        model=PersonModel(),
        accessor="directors",
        facet=True,
    )
    actors: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=PersonModel(),
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

    dates: FuzzyDateField = FuzzyDateField(field_name="date_range", optional=True)
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(performance, {"filter": {}, "exclude": {}})]
    collection_name = "performance"
    default_sorting_field = "title"


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


class PosterCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label", sort=True)
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
    default_models = [(Poster.objects.all(), {"filter": {}, "exclude": {}})]
    collection_name = "poster"
    default_sorting_field = "name"
