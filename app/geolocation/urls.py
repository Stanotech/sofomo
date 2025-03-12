from django.urls import path
from .views import GeolocationView

urlpatterns = [
    path("geolocation/", GeolocationView.as_view(), name="geolocation"),
]