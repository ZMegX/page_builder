from django.urls import path
from .views import address_list_create, map_view

urlpatterns = [
    path('api/addresses/', address_list_create, name='address-list-create'),
    path('', map_view, name='map_view'),

]