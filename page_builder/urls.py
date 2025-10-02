
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Documentation page - must be before catch-all patterns
    path('documentation/', user_views.documentation, name='documentation'),
    
    # Menus
    path('menus/', include('menus.urls', namespace='menus')),
    
    # React catch-all route for menu-editor (must be before slug catch-alls)
    path('menu-editor/', TemplateView.as_view(template_name='users/index.html'), name='react_menu_editor'),
    path('menu-editor/<path:path>/', TemplateView.as_view(template_name='users/index.html')),

    # Home page
    path('', user_views.home, name='home'),
    # Registration flow
    path('register/', user_views.register, name='register'),
    # Django's built-in authentication URLs (login, logout, password management)
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('users.urls')),
    path('locations/', include('locations.urls')),
    
    # Restaurant public pages and catch-all patterns - must be last
    path('', include('webpage_restaurant_site.urls')),
    path("", include("menus.public_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
