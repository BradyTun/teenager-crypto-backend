from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import *
from .otp_views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="user_registration_view"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "token/obtain/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("profile/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("request-otp/", RequestOTPAPI.as_view(), name="request_otp"),
    path("reset-password/", ResetPasswordAPI.as_view(), name="reset_password"),
    path("change-password/", PasswordResetView.as_view(), name="change_password"),

]
