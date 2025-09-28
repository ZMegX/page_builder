from .models import Order, Review
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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'reviewer_name', 'rating', 'is_approved', 'created_at')
    list_filter = ('restaurant', 'is_approved', 'rating')
    search_fields = ('reviewer_name', 'comment')