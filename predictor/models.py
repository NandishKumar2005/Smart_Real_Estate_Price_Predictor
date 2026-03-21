from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    average_price_per_sqft = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=255)
    area = models.FloatField()
    bhk = models.IntegerField()
    bathrooms = models.IntegerField()
    age = models.IntegerField()
    predicted_price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.location} - {self.bhk}BHK ({self.predicted_price})"

class PropertyListing(models.Model):
    title = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    area = models.FloatField()
    bhk = models.IntegerField()
    bathrooms = models.IntegerField()
    price = models.FloatField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class PropertyLocation(models.Model):
    location_name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    avg_price = models.FloatField()
    
    def __str__(self):
        return self.location_name
