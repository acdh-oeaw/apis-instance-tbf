from apis_acdhch_default_settings.urls import urlpatterns
from django.urls import include, path

from .api.tbit.urls import urlpatterns as tbit_urls

urlpatterns += [path("", include("django_interval.urls"))]
urlpatterns += tbit_urls
