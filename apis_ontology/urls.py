from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns += [
    path(
        "api/tbit/", include((router.urls, "apis_ontology.api.tbit"), namespace="tbit")
    ),
]
