from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name="register"),
    path('verify-email/', views.VerifyUserEmail.as_view(), name="verify"),
    path('login/', views.LoginUserView.as_view(), name="login"),
    path('test_login/', views.TestAuthenticationView.as_view(), name="granted"),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    # path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('set-new-password/', views.SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', views.LogoutApiView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.DecodeTokenView.as_view(), name='decode-token'),        
    # I think its better if create a seperate app just for profile views 
    
    # path('my-profile/', views.PrivateProfileView.as_view(), name='private-profile'),
    # path('profile/<int:user__id>/', views.PublicProfileView.as_view(), name='public-profile-detail'),
]
