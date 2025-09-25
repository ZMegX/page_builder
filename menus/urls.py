from django.urls import path, re_path
from .views import (
    MenuListView,
    MenuDetailView,
    MenuUpdateView,
    MenuDeleteView
)
from . import views
from .views_menu_items import add_menu_item, menu_item_detail
from rest_framework import routers
from .views import MenuViewSet, MenuItemViewSet

app_name = "menus"

router = routers.DefaultRouter()
router.register(r'api/menus', MenuViewSet)
router.register(r'api/menu-items', MenuItemViewSet)

urlpatterns = [
    path('create/', views.redirect_to_frontend_add_item, name='menu_create'),
    path('menus/', MenuListView.as_view(), name='menu_list'),
    path('<int:pk>/edit/', MenuUpdateView.as_view(), name='edit_menu'),    
    path('<int:pk>/delete/', MenuDeleteView.as_view(), name='delete_menu'),    
    path('<int:pk>/toggle-status/', views.toggle_menu_status, name='menu_toggle_status'),  # Changed to pk
    path('<int:pk>/duplicate/', views.menu_duplicate, name='menu_duplicate'),  # Changed to pk
    path('<int:pk>/export/', views.menu_export, name='menu_export'),  
    path('<int:menu_id>/items/add/', add_menu_item, name='menu_items_add'),  # Keep menu_id for clarity
    path('item/<int:item_id>/', menu_item_detail, name='menu_item_detail'),
    re_path(r'^(?!menu-editor/)(?P<slug>[^/]+)/$', views.public_menu_detail, name='public_menu_detail'),
    path('menus/<int:pk>/', MenuDetailView.as_view(), name='menu_detail'),    
    path("my/", views.my_menu, name="my_menu"), 
    path('api/menu-sections/', views.menu_sections_api, name='menu_sections_api'),
    path('api/menu-items/reorder/', views.menu_items_reorder_api, name='menu_items_reorder_api'),

] + router.urls
