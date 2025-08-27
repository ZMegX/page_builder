from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Registration flow
    path('register/', user_views.create_profile, name='register'),
    path('register/registration/complete_profile/', user_views.complete_profile, name='complete_profile'),

    # Django's built-in authentication URLs (login, logout, password management)
    path('accounts/', include('django.contrib.auth.urls')),
]