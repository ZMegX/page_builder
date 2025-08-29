from django.contrib import admin
from .models import RestaurantDetails

class RestaurantDetailsAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'registration_number', 'cuisine_type', 'phone_number')

admin.site.register(RestaurantDetails, RestaurantDetailsAdmin)