from django.urls import path
from . import views

app_name = "menus"

urlpatterns = [
    path('menu_list/', views.menu_list, name='menu_list'),
    path('create/', views.create_menu, name='menu_create'),
    path('<int:pk>/edit/', views.edit_menu, name='edit_menu'),  # Changed to pk
    path('<int:pk>/delete/', views.delete_menu, name='delete_menu'),  # Changed to pk
    path('<int:pk>/toggle-status/', views.toggle_menu_status, name='menu_toggle_status'),  # Changed to pk
    path('<int:pk>/duplicate/', views.menu_duplicate, name='menu_duplicate'),  # Changed to pk
    path('<int:pk>/export/', views.menu_export, name='menu_export'),  
    path('<int:menu_id>/items/add/', views.add_menu_item, name='menu_items_add'),  # Keep menu_id for clarity
    path('item/<int:item_id>/', views.menu_item_detail, name='menu_item_detail'),
    path('public/<int:menu_id>/', views.public_menu_detail, name='public_menu_detail'),
    path('menus/<int:pk>/', views.menu_detail, name='menu_detail'),
    path("my/", views.my_menu, name="my_menu"), 

]
