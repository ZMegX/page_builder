from django.contrib import admin
from users.models import RestaurantProfile

class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'registration_number', 'cuisine_type', 'phone_number', 'logo',  )
    list_filter = ('theme_choice', 'name',)
    search_fields = ('name', 'registration_number', 'cuisine_type', 'phone_number',)
admin.site.register(RestaurantProfile, RestaurantProfileAdmin)