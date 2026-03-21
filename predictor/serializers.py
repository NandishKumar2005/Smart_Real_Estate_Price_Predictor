from rest_framework import serializers

class PredictionRequestSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=255)
    area = serializers.FloatField(min_value=100)
    bhk = serializers.IntegerField(min_value=1)
    bathrooms = serializers.IntegerField(min_value=1)
    age = serializers.IntegerField(min_value=0)
