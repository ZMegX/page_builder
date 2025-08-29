from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

class SocialLink(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='social_links')
    name = models.CharField(max_length=50)   # e.g., 'Instagram'
    url = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.profile.company_name})"

class OpeningHour(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.CharField(max_length=10)  # e.g., 'Monday'
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.open_time} - {self.close_time}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)
    email = models.EmailField(max_length=254)
    addresses = models.ManyToManyField(Address, blank=True, related_name='profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
class RestaurantDetails(models.Model):
    class Meta:
        verbose_name = "Restaurant Detail"
        verbose_name_plural = "Restaurant Details"
        
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, related_name='restaurant_details')
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)


    def __str__(self):
        return f"{self.profile.user.username} Restaurant Details"