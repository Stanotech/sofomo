import requests
from django.db import OperationalError
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Geolocation
from .serializers import GeolocationSerializer

IPSTACK_API_KEY = "Your IPStack API key"  # Dodaj do settings i wczytuj z settings.IPSTACK_API_KEY

class GeolocationView(APIView):

    def get(self, request):
        ip = request.query_params.get('ip')
        url = request.query_params.get('url')

        if not ip and not url:
            return Response({"error": "Please give IP or URL."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            geolocation = Geolocation.objects.get(ip_address=ip) if ip else Geolocation.objects.get(url=url)
            serializer = GeolocationSerializer(geolocation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Geolocation.DoesNotExist:
            return Response({"error": "There is no data about this IP or URL."}, status=status.HTTP_404_NOT_FOUND)
        except OperationalError:
            return Response({"error": "Database is not available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)