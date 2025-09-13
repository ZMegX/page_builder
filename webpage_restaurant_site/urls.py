from django.urls import path
from . import views

app_name = "webpage_restaurant_site"

urlpatterns = [
    path("<slug:slug>/", views.restaurant_landing, name="landing"),
    path("<slug:slug>/menu/", views.restaurant_menu, name="menu"),
]