from django.urls import path
from forms import views

urlpatterns = [
    path("", views.home, name="home"),
]