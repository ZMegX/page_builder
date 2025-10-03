from django.urls import path, include
from users import views, views_restaurant
from django.contrib.auth import views as auth_views
from users.forms import CustomSetPasswordForm
from users.views_restaurant import (
    browse_restaurants, 
    leave_review, 
    restaurant_reviews,
)
from users.views_users import (
    order_detail,
    order_list,
)
from users.api_views import (
    CustomerOrderListView, CustomerOrderDetailView,
    RestaurantOrderListView, RestaurantOrderDetailView,
)

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', views.profile_manage, name='profile'),
    path('restaurant/profile/', views_restaurant.restaurant_profile, name='restaurant_profile'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/registration/password_reset_form.html',
        email_template_name='users/registration/password_reset_email.html',
    ), name='password_reset'),
    path(
    'password-reset-confirm/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        form_class=CustomSetPasswordForm
    ),
    name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('why-choose-us/', views.why_choose_us, name='why_choose_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('restaurants/', browse_restaurants, name='browse_restaurants'),
    path('review/<int:restaurant_pk>/', leave_review, name='leave_review'),
    # users/urls.py
    path('restaurant/<int:restaurant_pk>/reviews/', restaurant_reviews, name='restaurant_reviews'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/', order_list, name='order_list'),  # for order history
    path('restaurant/orders/', views.restaurant_orders_list, name='restaurant_orders_list'),
    path('restaurant/orders/<int:order_id>/', views_restaurant.restaurant_order_detail, name='restaurant_order_detail'),
    # review management
    path('restaurant/reviews/', views_restaurant.manage_reviews, name='manage_reviews'),
    path('review/<int:review_id>/reply/', views_restaurant.reply_to_review, name='reply_to_review'),

    # API endpoints
    path('api/orders/', CustomerOrderListView.as_view(), name='api_customer_orders'),
    path('api/orders/<int:pk>/', CustomerOrderDetailView.as_view(), name='api_customer_order_detail'),
    path('api/restaurant-orders/', RestaurantOrderListView.as_view(), name='api_restaurant_orders'),
    path('api/restaurant-orders/<int:pk>/', RestaurantOrderDetailView.as_view(), name='api_restaurant_order_detail'),
]