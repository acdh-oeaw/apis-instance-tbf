from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import include, path

urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += [path("api/tbit/", include("apis_ontology.api.tbit.urls"))]
urlpatterns.append(path("apis_typesense/", include("apis_typesense.urls")))
