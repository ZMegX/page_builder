from django.urls import path
from users.views_restaurant import browse_restaurants 
from menus.views import public_menu_detail
from . import views

app_name = "webpage_restaurant_site"

urlpatterns = [
    path('restaurants/', browse_restaurants, name='browse_restaurants'),        
    path("r/<slug:slug>/", views.restaurant_landing, name="landing"),
    path('r/<str:username>/', views.redirect_to_restaurant_slug, name='redirect_to_restaurant_slug'),
    path('cart/', views.cart_display, name='cart'),
    path('order/place/', views.place_order, name='place_order'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('<slug:slug>/', public_menu_detail, name='public_menu_detail'),
    path("<slug:slug>/menu/", views.restaurant_menu, name="menu"),
    path('<slug:slug>/order/', views.order_online, name='order_online'),

]
