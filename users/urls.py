from django.urls import path, include
from users import views

urlpatterns = [
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.create_profile, name="registration"),
    path('profile/', views.profile_view, name='profile'),

]