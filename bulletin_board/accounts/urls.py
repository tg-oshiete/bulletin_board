from django.urls import path
from . import views, views_email_otp

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views_email_otp.register_step1, name='register'),
    path('register/code/', views_email_otp.register_step2, name='register_code'),
    path('register/finalize/', views_email_otp.register_finalize, name='register_finalize'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),
    path('login/step1/', views.login_view, name='login_step1'),
    path('register/step1/', views_email_otp.register_step1, name='register_step1'),
    path('register/step2/', views_email_otp.register_step2, name='register_step2'),
]