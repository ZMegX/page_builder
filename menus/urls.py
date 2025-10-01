from django.urls import path, re_path
from .views import (
    MenuListView,
    MenuDetailView,
    MenuDeleteView,
)
from . import views
from .views_menu_items import add_menu_item, menu_item_detail
from rest_framework import routers
from .views import MenuViewSet, MenuItemViewSet
from users.views_restaurant import browse_restaurants

app_name = "menus"

router = routers.DefaultRouter()
router.register(r'api/menus', MenuViewSet)
router.register(r'api/menu-items', MenuItemViewSet)

urlpatterns = [
    path('', MenuListView.as_view(), name='menu_list'),
    path('<int:pk>/edit/', views.redirect_to_menu_editor, name='edit_menu'),
    path('<int:pk>/delete/', MenuDeleteView.as_view(), name='delete_menu'),    
    path('<int:pk>/toggle-status/', views.toggle_menu_status, name='menu_toggle_status'),
    path('<int:pk>/duplicate/', views.menu_duplicate, name='menu_duplicate'),
    path('<int:pk>/export/', views.menu_export, name='menu_export'),
    path('<int:menu_id>/items/add/', add_menu_item, name='menu_items_add'),
    path('item/<int:item_id>/', menu_item_detail, name='menu_item_detail'),
    path('restaurants/', browse_restaurants, name='browse_restaurants'),
    re_path(r'^(?!menu-editor/)(?P<slug>[^/]+)/$', views.public_menu_detail, name='public_menu_detail'),
    path('<int:pk>/', MenuDetailView.as_view(), name='menu_detail'),
    path("my/", views.my_menu, name="my_menu"),
    path('api/menu-sections/', views.menu_sections_api, name='menu_sections_api'),
    path('api/menu-items/reorder/', views.menu_items_reorder_api, name='menu_items_reorder_api'),

] + router.urls
