from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Registration flow
    path('register/', user_views.register, name='register'),
    # Django's built-in authentication URLs (login, logout, password management)
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('users.urls')),
    path('builder/', include('page_builder_app_create_page.urls', namespace='page_builder_app_create_page')),  # This makes your dashboard app the root page
    path("", include('menus.urls', namespace='menus')),
    path("", include("restaurant_site.urls", namespace="restaurant_site")),
    path("", include("menus.public_urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)