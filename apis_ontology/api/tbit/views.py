from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from apis_ontology.models import (
    Manifestation,
    PersonIsTranslatorOfExpression,
    Work,
)

from .serializers import (
    ManifestationSerializer,
    PersonIsTranslatorSerializer,
    WorkSerializer,
)


class TbitPagination(LimitOffsetPagination):
    """
    Default pagination class for TBit API endpoints.
    """

    pass


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = TbitPagination
    serializer_class = WorkSerializer
    queryset = Work.objects.all().exclude(tbit_category__exact="")


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = TbitPagination
    serializer_class = ManifestationSerializer
    queryset = Manifestation.objects.all().exclude(tbit_shelfmark__exact="")


class TranslatorViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = TbitPagination
    serializer_class = PersonIsTranslatorSerializer
    queryset = PersonIsTranslatorOfExpression.objects.order_by(
        "subj_object_id"
    ).distinct("subj_object_id")
