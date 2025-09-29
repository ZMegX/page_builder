from django.contrib import admin
from .models import UserAddress, CustomerAddress

admin.site.register(UserAddress)
admin.site.register(CustomerAddress)