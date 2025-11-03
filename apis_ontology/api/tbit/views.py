from rest_framework import viewsets

from apis_ontology.models import (
    Work,
)

from .serializers import (
    WorkSerializer,
)


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkSerializer
    queryset = Work.objects.all().exclude(tbit_category__exact="")
