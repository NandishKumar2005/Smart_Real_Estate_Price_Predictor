from django.contrib import admin
from .models import Location, PredictionHistory, PropertyListing, PropertyLocation

@admin.register(PropertyLocation)
class PropertyLocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'latitude', 'longitude', 'avg_price')
    search_fields = ('location_name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_price_per_sqft')
    search_fields = ('name',)

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('location', 'bhk', 'area', 'predicted_price', 'user', 'timestamp')
    list_filter = ('location', 'bhk', 'timestamp')
    search_fields = ('location', 'user__username')

@admin.register(PropertyListing)
class PropertyListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'bhk', 'price', 'created_at')
    list_filter = ('location', 'bhk')
    search_fields = ('title', 'location__name')
