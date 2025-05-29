from rest_framework import serializers

from .models import Geolocation
from .utils import is_valid_ip, is_valid_url


class GeolocationInputSerializer(serializers.Serializer):
    ip = serializers.CharField(required=False, allow_blank=True)
    url = serializers.CharField(required=False, allow_blank=True)

    def validate_ip(self, value):
        if value and not is_valid_ip(value):
            raise serializers.ValidationError("Invalid IP address format.")
        return value

    def validate_url(self, value):
        if value and not is_valid_url(value):
            raise serializers.ValidationError("Invalid URL format.")
        return value

    def validate(self, data):
        ip = data.get("ip")
        url = data.get("url")

        if not ip and not url:
            raise serializers.ValidationError("Please provide an IP or URL.")
        if ip and url:
            raise serializers.ValidationError("Provide either an IP or a URL, not both.")
        return data


class GeolocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocation
        fields = "__all__"