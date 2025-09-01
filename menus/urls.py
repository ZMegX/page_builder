from django.urls import path
from . import views

app_name = "menus"

urlpatterns = [
    path("menu/<int:menu_id>/items/", views.edit_menu_items, name="edit_menu_items"),
    path("menu/<int:menu_id>/", views.menu_detail, name="menu_detail"),
    path("menu/new/", views.create_menu, name="create_menu"),
]
