import re

from apis_core.generic.serializers import (
    GenericHyperlinkedModelSerializer,
    serializer_factory,
)
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import (
    IntegerField,
    SerializerMethodField,
)
from rest_framework.serializers import ModelSerializer, Serializer

from apis_ontology.models import (
    Manifestation,
    Person,
    PersonIsTranslatorOfExpression,
    Work,
)


class BaseModelSerializer(GenericHyperlinkedModelSerializer):
    """
    Base serializer for model classes.

    Adds an "id" field, which aliases an object's "pk".
    Also implicitly includes a "url" field, which points to the object's
    detail view.
    """

    id = IntegerField(source="pk")


class ShortTitleMixin(Serializer):
    """
    Mixin to recreate TBit "short_title" values from information (temporarily)
    stored in the "other_title_information" field, and to return the latter
    sans this information.

    When TBit data was imported, "short_title" values, where present, were
    added to the "other_title_information" field (which is meant to hold extra
    information like issue numbers/names etc.) in the form "(short title:
    $SHORT_TITLE_VALUE)" as a temporary measure so as not to lose any data.
    No separate field was created for "short_title"s because they appear only
    in conjunction with exceptionally long "title" values (which seem to include
    subtitles, for which there is actually a separate field), presumably
    to differentiate between "common" (shortened) titles and full titles.
    """

    short_title = SerializerMethodField()
    other_title_information = SerializerMethodField()  # overrides model field raw value

    def get_short_title(self, obj):
        """
        Extract TBit "short_title" information from "other_title_information"
        field (where that information exists), until long titles are sorted out.
        """
        if (
            other_title_info := obj.other_title_information
        ) and "short title" in other_title_info:
            if short_title := re.search(r"\(short title: (.*)\)", other_title_info):
                return short_title.group(1)

    def get_other_title_information(self, obj):
        """
        Return "other_title_information" field contents sans TBit "short_title"
        information, which was parked in the field.
        """
        if other_title_info := obj.other_title_information:
            manifestation_metadata = re.sub(
                r"\(short title: .*\)", "", other_title_info
            )
            if manifestation_metadata:
                return manifestation_metadata
        return ""


class WorkSerializer(BaseModelSerializer, ShortTitleMixin, ModelSerializer):
    """
    Serialize Work entity model to replicate objects in works.json.
    """

    class Meta:
        model = Work
        fields = ["id", "title", "short_title", "category", "url"]
        extra_kwargs = {
            "category": {"source": "tbit_category"},
        }


class ManifestationSerializer(BaseModelSerializer, ShortTitleMixin, ModelSerializer):
    """
    Serialize Manifestation entity model to replicate objects in publications.json.
    """

    language = SerializerMethodField()
    publication_details = SerializerMethodField()

    class Meta:
        model = Manifestation
        fields = [
            "id",
            "title",
            "short_title",
            "language",
            "publication_details",
            "signatur",
            "url",
        ]
        extra_kwargs = {
            "signatur": {"source": "tbit_shelfmark"},
        }

    def get_publication_details(self, obj):
        """
        Combine values stored in Manifestation fields "other_title_information"
        (sans info on TBit short titles, which are parked in the field)
        and "relevant_pages" to replicate TBit's "publication_details".

        publication_details concatenates the datapoints with a comma when
        both are present (i.e. "INFO, PAGES"), otherwise only contains one
        or the other.
        """
        publication_details = []

        if other_title_info := self.get_other_title_information(obj):
            publication_details.append(other_title_info)

        if relevant_pages := obj.relevant_pages:
            publication_details.append(relevant_pages)

        if publication_details:
            return ", ".join(publication_details)

    def get_language(self, obj):
        """
        Variation of IETF BCP 47 full language tag formatted for
        Thomas Bernhard in translation.

        TBit uses all-lowercase characters for language information as well as
        underscores instead of hyphens to separate subtags for primary language
        and varieties. This method combines any subtags into a full language
        tag using this format.

        Examples: "en" for English,
                  "pt_br" (instead of pt-BR) for Brazilian Portuguese.

        :return: lowercased full language tag, separating base language
                 from varieties with underscores, e.g. "en", "pt_br"
        :rtype: str
        """
        primary_language = obj.primary_language.lower() or ""
        variety = obj.variety.lower() or ""

        if not primary_language:
            return ""

        if not variety:
            return primary_language

        return f"{primary_language}_{variety}"

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # remove key used by, but not required by TBit if empty
        if ret["publication_details"] is None:
            ret.pop("publication_details")

        return ret


class PersonSerializer(BaseModelSerializer, ModelSerializer):
    """
    Serialize Person entity model for use in PersonIsTranslatorSerializer.
    """

    name = SerializerMethodField()  # name field used by TBit

    class Meta:
        model = Person
        fields = [
            "id",
            "url",
            "name",
        ]

    def get_name(self, obj):
        """
        Recreate TBit's "name" value by concatenating a Person's forename and
        surname to their full name in the form "SURNAME, FORENAME".
        """
        tbit_name = ""
        surname = obj.surname
        forename = obj.forename

        if forename != "" and surname != "":
            tbit_name = f"{surname}, {forename}"
        elif surname != "":
            tbit_name = surname
        elif forename != "":
            tbit_name = forename
        else:
            pass

        return tbit_name


class PersonIsTranslatorSerializer(BaseModelSerializer, ModelSerializer):
    """
    Serialize PersonIsTranslatorOfExpression relation model to use as basis
    for replicating objects in translators.json.
    """

    person = SerializerMethodField(allow_null=False)

    class Meta:
        model = PersonIsTranslatorOfExpression
        fields = [
            "id",
            "url",
            "person",
        ]

    @extend_schema_field(PersonSerializer())
    def get_person(self, obj):
        if obj.subj:
            serializer = serializer_factory(type(obj.subj), PersonSerializer)
            return serializer(
                obj.subj, context={"request": self.context["request"]}
            ).data

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        person = representation.pop("person")
        for key in person:
            representation[key] = person[key]
        return representation
