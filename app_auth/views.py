from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from django.contrib.auth.hashers import check_password

User = get_user_model()

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegistrationView(APIView):
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        request_body=RegistrationSerializer,
        responses={
            status.HTTP_201_CREATED: "Registration successful",
            status.HTTP_409_CONFLICT: "Account with that email already exists",
            status.HTTP_400_BAD_REQUEST: "Invalid data provided",
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                return Response(
                    {
                        "message": "Registration successful",
                        "user": CustomUserSerializer(user).data,
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    {
                        "message": "Account with that email already exists",
                    },
                    status=status.HTTP_409_CONFLICT,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Extract IP address from request
        ip_address = self.get_client_ip(request)

        # Update last login IP of the user
        user.last_login_ip = ip_address
        user.save(update_fields=["last_login_ip"])

        # Check if the user is a super admin
        if user.is_superuser:
            # Get FCM registration token from request headers or data
            fcm_registration_token = request.headers.get("X-FCM-Token") or request.data.get("fcm_token")

            if fcm_registration_token:
                # Save the token to the user's profile for FCM notifications
                user.fcm_registration_token = fcm_registration_token
                user.save(update_fields=["fcm_registration_token"])

        try:
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PasswordResetView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Reset password by providing old and new passwords",
        request_body=PasswordResetSerializer,
        responses={
            200: "Password reset successful",
            400: "Invalid data or incorrect old password",
        },
    )
    def post(self, request):
        user = request.user
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Check if the old password is correct
            if not check_password(old_password, user.password):
                return Response(
                    {"detail": "Incorrect old password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set the new password
            user.set_password(new_password)
            user.save()

            return Response(
                {"detail": "Password reset successful."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update user profile information",
        request_body=UserUpdateSerializer,
        responses={
            200: CustomUserSerializer,
            400: "Invalid data provided",
        },
    )
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
