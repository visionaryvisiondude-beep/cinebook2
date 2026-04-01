"""
AUTH ENDPOINTS
==============
POST   /api/auth/register/           Register a new user
POST   /api/auth/login/              Login → access + refresh JWT
POST   /api/auth/logout/             Blacklist refresh token
POST   /api/auth/token/refresh/      Get new access token from refresh token
GET    /api/auth/profile/            Get own profile
PUT    /api/auth/profile/            Full update profile
PATCH  /api/auth/profile/            Partial update profile
POST   /api/auth/change-password/    Change password
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView

app_name = 'users'

urlpatterns = [
    path('register/',        RegisterView.as_view(),        name='register'),
    path('login/',           LoginView.as_view(),           name='login'),
    path('logout/',          LogoutView.as_view(),          name='logout'),
    path('token/refresh/',   TokenRefreshView.as_view(),    name='token-refresh'),
    path('profile/',         ProfileView.as_view(),         name='profile'),
    path('change-password/', ChangePasswordView.as_view(),  name='change-password'),
]
