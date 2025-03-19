from django.db import models


class Geolocation(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    url = models.URLField(null=True, blank=True, db_index=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address or self.url
