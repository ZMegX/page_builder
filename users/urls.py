from django.urls import path, include
from users import views
from django.contrib.auth import views as auth_views
from users.forms import CustomSetPasswordForm

urlpatterns = [
    path('register/', views.register, name='register'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('profile/', views.profile_manage, name='profile'),
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
]