from .models import Order
from django.contrib import admin
from users.models import RestaurantProfile

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer__username', 'restaurant__name', 'id')
    
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'registration_number', 'cuisine_type', 'phone_number', 'logo',  )
    list_filter = ('theme_choice', 'name',)
    search_fields = ('name', 'registration_number', 'cuisine_type', 'phone_number',)
admin.site.register(RestaurantProfile, RestaurantProfileAdmin)