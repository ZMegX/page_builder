from django.urls import path
from .views import map_view
from . import views

app_name = 'locations'

urlpatterns = [
    path('api/addresses/', views.address_list_create, name='address-list-create'),
    path('api/addresses/<int:pk>/delete/', views.address_delete, name='address-delete'),
    path('', map_view, name='map_view'),

]