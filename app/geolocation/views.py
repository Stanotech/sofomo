from functools import wraps
from typing import Optional, Tuple

import requests
from django.conf import settings
from django.db import DatabaseError, OperationalError
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Geolocation
from .serializers import GeolocationSerializer
from .utils import is_valid_ip, is_valid_url


def handle_db_error(func: callable) -> callable:
    """
    Dekorator for handle database errors.
    """

    @wraps(func)
    def wrapper(self: "GeolocationView", request: Request, *args: tuple, **kwargs: dict) -> Response:
        try:
            return func(self, request, *args, **kwargs)
        except (OperationalError, DatabaseError) as e:
            return Response(
                {"error": f"{str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    return wrapper


class GeolocationView(APIView):
    """
    API endpoint to retrieve and store geolocation data for IP addresses and URLs.
    """

    @handle_db_error
    def get(self, request: Request) -> Response:
        """
        Retrieve geolocation data for a given IP or URL.
        """

        ip, url, error_response = self._get_ip_or_url(request)
        if error_response:
            return error_response

        geolocations = self._get_geolocations(ip, url)
        if not geolocations:
            return Response(
                {"error": "No data found for this IP or URL."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = GeolocationSerializer(geolocations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_db_error
    def post(self, request: Request) -> Response:
        """
        Retrieve and store geolocation data for the given IP or URL.
        """

        if not settings.IPSTACK_API_KEY:
            return Response(
                {"error": "Missing IPStack API key in settings."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        ip, url, error_response = self._get_ip_or_url(request)
        if error_response:
            return error_response

        geolocation_data = self._get_geolocation_data_from_ipstack(ip, url)
        if isinstance(geolocation_data, Response):
            return geolocation_data

        geolocation = Geolocation.objects.create(
            ip_address=ip or None,
            url=url or None,
            country=geolocation_data.get("country_name", ""),
            region=geolocation_data.get("region_name", ""),
            city=geolocation_data.get("city", ""),
            latitude=geolocation_data.get("latitude", 0),
            longitude=geolocation_data.get("longitude", 0),
        )
        serializer = GeolocationSerializer(geolocation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @handle_db_error
    def delete(self, request: Request) -> Response:
        """
        Delete geolocation data for a given IP or URL.
        """

        ip, url, error_response = self._get_ip_or_url(request)
        if error_response:
            return error_response

        deleted, _ = self._get_geolocations(ip, url).delete()
        if deleted == 0:
            return Response(
                {"error": "Data not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_ip_or_url(self, request: Request) -> Tuple[Optional[str], Optional[str], Optional[Response]]:
        """
        Helper function to extract and validate IP or URL from the request.
        """

        ip = request.query_params.get("ip") or request.data.get("ip")
        url = request.query_params.get("url") or request.data.get("url")

        if not ip and not url:
            error_msg = "Please provide an IP or URL."
        elif ip and url:
            error_msg = "Provide either an IP or a URL, not both."
        elif ip and not is_valid_ip(ip):
            error_msg = "Invalid IP address format."
        elif url and not is_valid_url(url):
            error_msg = "Invalid URL format."
        else:
            return ip, url, None

        return None, None, Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

    def _get_geolocations(self, ip: str | None, url: str | None) -> QuerySet:
        """
        Helper function to filter geolocation records by IP or URL.
        Only one parameter (either IP or URL) is processed,
        as the helper _get_ip_or_url ensures that both are not provided at the same time.
        """

        if ip:
            return Geolocation.objects.filter(ip_address=ip)
        elif url:
            return Geolocation.objects.filter(url=url)

    def _get_geolocation_data_from_ipstack(self, ip: str | None, url: str | None) -> dict | Response:
        """
        Helper function to retrieve geolocation data from the IPStack API.
        """
        ipstack_url = f"https://api.ipstack.com/{ip or url}?access_key={settings.IPSTACK_API_KEY}"
        response = requests.get(ipstack_url, timeout=5)

        if response.status_code != 200:
            return Response(
                {
                    "error": "IPStack API error",
                    "status_code": response.status_code,
                    "details": response.text,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            data = response.json()
        except ValueError:
            return Response(
                {"error": "Invalid JSON response from IPStack API"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not data.get("success", True):
            return Response(
                {
                    "error": "IPStack API returned an error",
                    "details": data.get("error", {}).get("info", "Unknown error")
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        required_keys = [
            "country_name",
            "region_name",
            "city",
            "latitude",
            "longitude",
        ]

        if not all(key in data for key in required_keys):
            return Response(
                {"error": "Invalid data from IPStack API"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return data
