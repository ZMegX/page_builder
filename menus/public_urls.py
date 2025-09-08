from django.urls import path
from . import views

app_name = "restaurant_site"

urlpatterns = [
    # e.g. /r/<username>/menu/
    path("r/<slug:slug>/menu/", views.public_menu_detail, name="menu"),
]