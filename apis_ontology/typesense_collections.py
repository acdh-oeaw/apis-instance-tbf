from apis_typesense.collections import BaseCollection
from apis_typesense.fields import (
    EnumField,
    FixedStringField,
    FuzzyDateField,
    SameAsField,
    TypesenseField,
)
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat

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

works = Work.objects.all().annotate(
    author=ArraySubquery(author_of),
)
manifest = Manifestation.objects.filter(id=OuterRef("subj_object_id"))[:1]
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

perf_work = PerformancePerformedWork.objects.filter(subj_object_id=OuterRef("id"))[:1]
perf_direct = PerformanceHadDirectorPerson.objects.filter(subj_object_id=OuterRef("id"))
perf_actor = PerformanceHadParticipantPerson.objects.filter(
    subj_object_id=OuterRef("id")
)
poster_perf = PosterPromotedEvent.objects.filter(obj_object_id=OuterRef("id"))
perf_group = PerformanceHadParticipantGroup.objects.filter(
    subj_object_id=OuterRef("id")
)
performance = Performance.objects.all().annotate(
    work_id=Subquery(perf_work.values("obj_object_id")),
    directors=ArraySubquery(perf_direct.values_list("obj_object_id", flat=True)),
    actors=ArraySubquery(perf_actor.values_list("obj_object_id", flat=True)),
    posters=ArraySubquery(poster_perf.values_list("subj_object_id", flat=True)),
    theaters=ArraySubquery(perf_group.values_list("obj_object_id", flat=True)),
)


class WorkCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    category: TypesenseField = TypesenseField(
        type="string", field_name="tbit_category", optional=True
    )
    author_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="author",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")

    default_models = [(works, {"filter": {}, "exclude": {}})]
    collection_name = "work"


class ExpressionCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    language: EnumField = EnumField(
        source="index",
        type="string",
        field_name="language_man",
    )
    type: FixedStringField = FixedStringField(value="expression", type="string")
    translator_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="transl",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
    )
    year: TypesenseField = TypesenseField(
        type="int32", optional=True, field_name="year"
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(expressions, {"filter": {}, "exclude": {}})]
    collection_name = "expression"


class PerformanceCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    work_id: TypesenseField = TypesenseField(
        type="string",
        field_name="work_id",
        reference="tbo_work.id",
        async_reference=True,
        cascade_delete=False,
    )
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="label")
    type: FixedStringField = FixedStringField(value="performance", type="string")
    director_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="directors",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
    )
    actor_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="actors",
        reference="tbo_person.id",
        async_reference=True,
        cascade_delete=False,
    )
    poster_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="posters",
        reference="tbo_poster.id",
        async_reference=True,
        cascade_delete=False,
    )
    theater_ids: TypesenseField = TypesenseField(
        type="string[]",
        optional=True,
        field_name="theaters",
        reference="tbo_group.id",
        async_reference=True,
        cascade_delete=False,
    )

    dates: FuzzyDateField = FuzzyDateField(field_name="date_range", optional=True)
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(performance, {"filter": {}, "exclude": {}})]
    collection_name = "performance"


class PersonCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label")
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(persons, {"filter": {}, "exclude": {}})]
    collection_name = "person"


class GroupCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label")
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(Group.objects.all(), {"filter": {}, "exclude": {}})]
    collection_name = "group"


class PosterCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    name: TypesenseField = TypesenseField(type="string", field_name="label")
    year: TypesenseField = TypesenseField(
        type="int32", field_name="year", optional=True
    )
    country: EnumField = EnumField(
        type="string", field_name="country", source="index", optional=True
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")
    default_models = [(Poster.objects.all(), {"filter": {}, "exclude": {}})]
    collection_name = "poster"
