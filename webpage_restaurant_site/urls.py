from django.urls import path
from . import views

app_name = "webpage_restaurant_site"

urlpatterns = [
    path("r/<slug:slug>/", views.landing, name="landing"),
    path("r/<slug:slug>/menu/", views.restaurant_menu, name="menu"),
]