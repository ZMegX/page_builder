from django.urls import path
from page_builder_app_create_page import views

app_name = 'page_builder_app_create_page'

urlpatterns = [
    path('', views.builder_home, name='builder_home'),
    path('builder/<slug:template_slug>/', views.webpage_builder, name='webpage_builder'),
    path('my-pages/', views.my_webpages, name='my_webpages'),
    path('page/<int:webpage_id>/', views.render_webpage, name='render_webpage'),
]