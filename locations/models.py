from django.db import models

class UserAddress(models.Model):
    """
    Stores an address with its geographic coordinates.
    """
    restaurant_profile = models.ForeignKey(
            'users.RestaurantProfile', 
            on_delete=models.CASCADE, 
            related_name="delivery_addresses"
        )    
    formatted_address = models.CharField(max_length=255, help_text="The full, formatted address returned by Google.")
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.formatted_address

    class Meta:
        verbose_name_plural = "Addresses"
