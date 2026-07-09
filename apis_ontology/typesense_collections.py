from apis_typesense.collections import BaseCollection
from apis_typesense.fields import EnumField, SameAsField, TypesenseField
from apis_typesense.models import ModelField, ModelSerializer
from django.contrib.postgres.expressions import ArraySubquery, Subquery
from django.db.models import OuterRef, Value
from django.db.models.functions import Concat, JSONObject

from apis_ontology.models import (
    Expression,
    Performance,
    PerformancePerformedWork,
    Person,
    PersonIsAuthorOfWork,
    Work,
    WorkIsRealisedInExpression,
)

expression = Expression.objects.filter(pk=OuterRef("obj_object_id"))
persons = Person.objects.filter(pk=OuterRef("subj_object_id")).annotate(
    label=Concat("forename", Value(" "), "surname")
)
performance = Performance.objects.filter(pk=OuterRef("subj_object_id"))
expr_realised_in = (
    WorkIsRealisedInExpression.objects.filter(subj_object_id=OuterRef("pk"))
    .annotate(
        exp_id=Subquery(expression[:1].values("id")),
        exp_title=Subquery(expression[:1].values("title")),
        exp_lang=Subquery(expression[:1].values("language")),
    )
    .values(json=JSONObject(id="exp_id", title="exp_title", language="exp_lang"))
)
author_of = (
    PersonIsAuthorOfWork.objects.filter(obj_object_id=OuterRef("pk"))
    .annotate(
        aut_id=Subquery(persons[:1].values("id")),
        aut_label=Subquery(persons[:1].values("label")),
    )
    .values(json=JSONObject(id="aut_id", label="aut_label"))
)
performed = (
    PerformancePerformedWork.objects.filter(obj_object_id=OuterRef("pk"))
    .annotate(
        pf_id=Subquery(performance[:1].values("id")),
        pf_label=Subquery(performance[:1].values("label")),
        pf_date=Subquery(performance[:1].values("date_range")),
    )
    .values(json=JSONObject(id="pf_id", label="pf_label", date="pf_date"))
)

works = Work.objects.all().annotate(
    realised_in=ArraySubquery(expr_realised_in),
    author=ArraySubquery(author_of),
    performances=ArraySubquery(performed),
)


class ExpressionModel(ModelSerializer):
    id: TypesenseField = TypesenseField(type="string", field_name="id")
    title: TypesenseField = TypesenseField(type="string", field_name="title")
    language: EnumField = EnumField(
        source="index",
        type="string",
        field_name="language",
    )


class PersonModel(ModelSerializer):
    id: TypesenseField = TypesenseField(type="string", field_name="id")
    name: TypesenseField = TypesenseField(type="string", field_name="label")


class PerformanceModel(ModelSerializer):
    id: TypesenseField = TypesenseField(type="string", field_name="id")
    label: TypesenseField = TypesenseField(type="string", field_name="label")
    date: TypesenseField = TypesenseField(type="string", field_name="date_range")


class WorkCollection(BaseCollection):
    id: TypesenseField = TypesenseField(type="string", field_name="pk")
    title: TypesenseField = TypesenseField(type="string", sort=True, field_name="title")
    category: TypesenseField = TypesenseField(
        type="string", field_name="tbit_category", optional=True
    )
    expressions: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=ExpressionModel(),
        accessor="realised_in",
    )
    authors: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=PersonModel(),
        accessor="author",
    )
    performances: ModelField = ModelField(
        type="object[]",
        optional=True,
        model=PerformanceModel(),
        accessor="performances",
    )
    sameas: SameAsField = SameAsField(domain="tb-online.acdh-dev.oeaw.ac.at")

    default_models = [(works, {"filter": {}, "exclude": {}})]
    collection_name = "work"
