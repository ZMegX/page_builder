from rest_framework import serializers
from locations.models import UserAddress

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'formatted_address', 'latitude', 'longitude', 'restaurant_profile']

