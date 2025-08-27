from django.urls import path, include
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile_manage, name='profile'),

]