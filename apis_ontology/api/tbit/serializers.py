import re

from apis_core.generic.serializers import (
    GenericHyperlinkedModelSerializer,
)
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from apis_ontology.models import (
    Manifestation,
    Work,
)


class BaseEntitySerializer(GenericHyperlinkedModelSerializer):
    """
    Base serializer class for entities.

    Adds a field for the object ID (i.e. pk) and the URL to an entity object's
    detail view.
    """

    id = IntegerField(source="pk")


class WorkSerializer(BaseEntitySerializer, ModelSerializer):
    short_title = SerializerMethodField()

    class Meta:
        model = Work
        fields = ["id", "title", "short_title", "category", "url"]
        extra_kwargs = {
            "category": {"source": "tbit_category"},
        }

    def get_short_title(self, obj):
        if (
            other_title_info := obj.other_title_information
        ) and "short title" in other_title_info:
            if short_title := re.search(r"\(short title: (.*)\)", other_title_info):
                return short_title.group(1)


class ManifestationSerializer(BaseEntitySerializer, ModelSerializer):
    short_title = SerializerMethodField()
    publication_details = SerializerMethodField()
    other_title_information = SerializerMethodField()  # overrides model field raw value

    class Meta:
        model = Manifestation
        fields = [
            "id",
            "title",
            "relevant_pages",  # included so it can be used over publication_details
            "other_title_information",  # included so it can be used over publication_details
            "short_title",
            "publication_details",
            "signatur",
            "url",
        ]
        extra_kwargs = {
            "signatur": {"source": "tbit_shelfmark"},
        }

    def to_representation(self, instance):
        """
        Remove "publication_details" key if it contains no data.

        Replicates data representation in TBit publications.json.
        """
        ret = super().to_representation(instance)

        if ret["publication_details"] is None:
            ret.pop("publication_details")

        return ret

    def get_other_title_information(self, obj):
        """
        Return Manifestation field "other_title_information" sans temporarily
        stored info on short titles.

        Filters out occurrences of "(short title: $SHORT_TITLE_VALUE)" substring
        and returns any remaining field contents, which may include further
        information about Manifestations, like issue names, issue numbers etc.
        """
        if other_title_info := obj.other_title_information:
            manifestation_metadata = re.sub(
                r"\(short title: .*\)", "", other_title_info
            )
            if manifestation_metadata:
                return manifestation_metadata
        return ""

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

    def get_short_title(self, obj):
        """
        Extract TBit "short_title" info (if it exists) from Manifestation field
        "other_title_information", where it was added in the form
        "(short title: $SHORT_TITLE_VALUE)" until long titles are sorted out.

        The assumption is long TBit titles include subtitles, which need manual
        saving/transferring to the subtitles field following a review.
        """
        if (
            other_title_info := obj.other_title_information
        ) and "short title" in other_title_info:
            if short_title := re.search(r"\(short title: (.*)\)", other_title_info):
                return short_title.group(1)
