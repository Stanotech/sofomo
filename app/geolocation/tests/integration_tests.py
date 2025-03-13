import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from geolocation.models import Geolocation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_integration_get_geolocation_by_ip(api_client):

    # creating test data
    Geolocation.objects.create(
        ip_address="192.168.1.1",
        country="Poland",
        region="Mazovia",
        city="Warsaw",
        latitude=52.2297,
        longitude=21.0122,
    )

    response = api_client.get(reverse("geolocation"), {"ip": "192.168.1.1"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["ip_address"] == "192.168.1.1"
    assert response.data[0]["city"] == "Warsaw"