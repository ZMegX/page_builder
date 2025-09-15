from django.urls import path
from users.views_restaurant import browse_restaurants 
from . import views

app_name = "webpage_restaurant_site"

urlpatterns = [
    path('restaurants/', browse_restaurants, name='browse_restaurants'), 
    path("<slug:slug>/", views.restaurant_landing, name="landing"),
    path("<slug:slug>/menu/", views.restaurant_menu, name="menu"),

]