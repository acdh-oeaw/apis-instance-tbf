from apis_acdhch_default_settings.urls import urlpatterns

from .api.tbit.urls import urlpatterns as tbit_urls

urlpatterns += tbit_urls
