"""
URLs relevant to API endpoints provided for Thomas Bernhard in translation.
"""

from django.urls import include, path
from rest_framework import routers

from apis_ontology.api.tbit.views import (
    PublicationViewSet,
    TranslatorViewSet,
    WorkViewSet,
)

router = routers.DefaultRouter()

router.register(r"works", WorkViewSet, basename="work")
router.register(r"publications", PublicationViewSet, basename="publication")
router.register(r"translators", TranslatorViewSet, basename="translator")

urlpatterns = [
    path("api/tbit/", include((router.urls, "apis_ontology"))),
]
