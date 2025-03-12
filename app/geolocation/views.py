import requests
from django.db import OperationalError
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Geolocation
from .serializers import GeolocationSerializer

IPSTACK_API_KEY = (
    "Your IPStack API key"  # Dodaj do settings i wczytuj z settings.IPSTACK_API_KEY
)


class GeolocationView(APIView):

    def get(self, request):
        ip = request.query_params.get("ip")
        url = request.query_params.get("url")

        if not ip and not url:
            return Response(
                {"error": "Please give IP or URL."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            geolocation = (
                Geolocation.objects.get(ip_address=ip)
                if ip
                else Geolocation.objects.get(url=url)
            )
            serializer = GeolocationSerializer(geolocation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Geolocation.DoesNotExist:
            return Response(
                {"error": "There is no data about this IP or URL."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except OperationalError:
            return Response(
                {"error": "Database is not available"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    
    def post(self, request):
        ip = request.data.get('ip')
        url = request.data.get('url')

        if not ip and not url:
            return Response({"error": "Please give IP or URL."}, status=status.HTTP_400_BAD_REQUEST)

        ipstack_url = f"http://api.ipstack.com/{ip or url}?access_key={IPSTACK_API_KEY}"
        response = requests.get(ipstack_url)

        if response.status_code != 200:
            return Response({"error": "IPStack API error"}, status=status.HTTP_502_BAD_GATEWAY)

        data = response.json()

        geolocation = Geolocation.objects.create(
            ip_address=ip if ip else None,
            url=url if url else None,
            country=data.get("country_name", ""),
            region=data.get("region_name", ""),
            city=data.get("city", ""),
            latitude=data.get("latitude", 0),
            longitude=data.get("longitude", 0),
        )

        serializer = GeolocationSerializer(geolocation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
