from django.urls import path
from page_builder_app_create_page import views

urlpatterns = [
    path("", views.home, name="home"),
]