from django.urls import path
from page_builder_app_create_page import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('builder/<slug:template_slug>/', views.webpage_builder, name='webpage_builder'),
    path('my-pages/', views.my_webpages, name='my_webpages'),
    path('page/<int:webpage_id>/', views.render_webpage, name='render_webpage'),
]