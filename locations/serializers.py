from rest_framework import serializers
from locations.models import UserAddress

class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.
    """
    class Meta:
        model = UserAddress
        # These are the fields that will be converted to/from JSON
        fields = ['id', 'formatted_address', 'latitude', 'longitude', 'restaurant_profile']
        
        # The 'restaurant_profile' is determined by the logged-in user in the view,
        # so it should not be editable by the client through the API.
        read_only_fields = ['restaurant_profile']
