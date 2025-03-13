import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from geolocation.views import GeolocationView
from geolocation.models import Geolocation
from geolocation.serializers import GeolocationSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.mark.django_db
def test_get_geolocation_by_ip(api_client, request_factory):

    # creating test data
    Geolocation.objects.create(
        ip_address="192.168.1.1",
        country="Poland",
        region="Mazovia",
        city="Warsaw",
        latitude=52.2297,
        longitude=21.0122,
    )

    request = request_factory.get("/geolocation/", {"ip": "192.168.1.1"})
    view = GeolocationView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["ip_address"] == "192.168.1.1"
    assert response.data[0]["city"] == "Warsaw"


@pytest.mark.django_db
def test_get_geolocation_by_url(api_client, request_factory):

    # creating test data
    Geolocation.objects.create(
        url="example.com",
        country="USA",
        region="California",
        city="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
    )

    request = request_factory.get("/geolocation/", {"url": "example.com"})
    view = GeolocationView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["url"] == "example.com"
    assert response.data[0]["city"] == "Los Angeles"


@pytest.mark.django_db
def test_get_geolocation_not_found(api_client, request_factory):

    # creating request with non-existent IP
    request = request_factory.get("/geolocation/", {"ip": "10.0.0.1"})
    view = GeolocationView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "No data found for this IP or URL."