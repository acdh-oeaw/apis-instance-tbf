import re

from apis_core.generic.serializers import (
    GenericHyperlinkedModelSerializer,
)
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from apis_ontology.models import (
    Work,
)


class WorkSerializer(GenericHyperlinkedModelSerializer, ModelSerializer):
    category = SerializerMethodField()
    short_title = SerializerMethodField()

    class Meta:
        model = Work
        fields = ["id", "title", "short_title", "category", "url"]

    def get_category(self, obj):
        return obj.tbit_category

    def get_short_title(self, obj):
        if (
            other_title_info := obj.other_title_information
        ) and "short title" in other_title_info:
            if short_title := re.search(r"\(short title: (.*)\)", other_title_info):
                return short_title.group(1)
