from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import APIClient

from geolocation.models import Geolocation
from geolocation.views import GeolocationView


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


@pytest.mark.django_db
def test_post_geolocation(api_client, request_factory):

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "country_name": "Poland",
        "region_name": "Mazovia",
        "city": "Warsaw",
        "latitude": 52.2297,
        "longitude": 21.0122,
    }

    with patch("requests.get", return_value=mock_response):
        request = request_factory.post("/geolocation/", {"ip": "192.168.1.1"})
        view = GeolocationView.as_view()

        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["ip_address"] == "192.168.1.1"
        assert response.data["city"] == "Warsaw"


@pytest.mark.django_db
def test_delete_geolocation(api_client, request_factory):

    Geolocation.objects.create(
        ip_address="192.168.1.1",
        country="Poland",
        region="Mazovia",
        city="Warsaw",
        latitude=52.2297,
        longitude=21.0122,
    )

    request = request_factory.delete("/geolocation/?ip=192.168.1.1")
    view = GeolocationView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Geolocation.objects.filter(ip_address="192.168.1.1").exists()


@pytest.mark.django_db
def test_post_geolocation_ipstack_error(api_client, request_factory):

    mock_response = MagicMock()
    mock_response.status_code = 502
    mock_response.json.return_value = {"error": "Internal Server Error"}

    with patch("requests.get", return_value=mock_response):
        request = request_factory.post("/geolocation/", {"ip": "192.168.1.1"})
        view = GeolocationView.as_view()

        response = view(request)

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["error"] == "IPStack API error"


@pytest.mark.django_db
def test_get_geolocation_invalid_ip(api_client, request_factory):
    request = request_factory.get("/geolocation/", {"ip": "invalid_ip"})
    view = GeolocationView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid IP address format."


@pytest.mark.django_db
def test_post_geolocation_invalid_ipstack_data(api_client, request_factory):

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "latitude": 52.2297,
        "longitude": 21.0122,
        # No "country_name" key
    }

    with patch("requests.get", return_value=mock_response):
        request = request_factory.post("/geolocation/", {"ip": "192.168.1.1"})
        view = GeolocationView.as_view()

        response = view(request)

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.data["error"] == "Invalid data from IPStack API"