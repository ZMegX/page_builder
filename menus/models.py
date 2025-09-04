from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cloudinary.models import CloudinaryField
from users.models import RestaurantProfile




class Menu(models.Model):
    restaurant = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)  # e.g. "Dinner Menu", "Lunch Specials"
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # useful if they have seasonal menus
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("restaurant", "name")  # one menu name per restaurant
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    image = CloudinaryField('image', blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # works well with Postgres
    is_available = models.BooleanField(default=True)
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="E.g. Appetizer, Main, Dessert"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.menu.name})"