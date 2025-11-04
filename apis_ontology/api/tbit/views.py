from rest_framework import viewsets

from apis_ontology.models import (
    Manifestation,
    Work,
)

from .serializers import (
    ManifestationSerializer,
    WorkSerializer,
)


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkSerializer
    queryset = Work.objects.all().exclude(tbit_category__exact="")


class ManifestationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ManifestationSerializer
    queryset = Manifestation.objects.all().exclude(tbit_shelfmark__exact="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = f"Publication {self.suffix}"
