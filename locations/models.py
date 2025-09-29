from django.db import models

class UserAddress(models.Model):
    """
    Stores an address with its geographic coordinates.
    """
    restaurant_profile = models.ForeignKey(
            'users.RestaurantProfile', 
            on_delete=models.CASCADE, 
            related_name="addresses"
        )    
    formatted_address = models.CharField(max_length=255, help_text="The full, formatted address returned by Google.")
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.formatted_address


class CustomerAddress(models.Model):
    customer_profile = models.ForeignKey(
        'users.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    formatted_address = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.formatted_address
