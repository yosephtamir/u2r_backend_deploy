from django.urls import path
from . import views

urlpatterns = [
    path('auth/signup/', views.RegistrationAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/login/refresh/', views.LoginRefreshView.as_view(), name='login_refresh'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('auth/check-email/', views.CheckEmailView.as_view(), name='check_email'),
    path('auth/authorize/', views.AuthorizeView.as_view(), name='authorize'),

    path('users/<int:user_id>/profile/', views.UserInformation.as_view(), name='user_profile_information'),
]
