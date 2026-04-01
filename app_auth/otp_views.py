from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, OTP

import os 

class RequestOTPAPI(APIView):
    @swagger_auto_schema(
        operation_description="Request an OTP for password reset or sign up",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
            },
        ),
        responses={
            200: openapi.Response(description="OTP sent to your email"),
        },
    )
    def post(self, request):
        email = request.data.get("email")

        # Check if the email exists in the User model
        user_exists = User.objects.filter(email=email).exists()

        # Generate or fetch an OTP
        otp_obj, _ = OTP.objects.get_or_create(email=email)
        otp = otp_obj.get_token()

        # Set the email subject and message based on the context
        if user_exists:
            subject = "Binance Trading - OTP for Password Reset"
            message_type = "reset your password"
        else:
            subject = "Binance Trading - OTP for Account Sign-Up"
            message_type = "create your account"

        message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #121212; color: #EAEAEA; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1C1C1C; padding: 20px; border-radius: 8px;">
                <h1 style="text-align: center; color: #FFD700;">Welcome!</h1>
                <p>Hello,</p>
                <p>You requested to {message_type}. Please enter the following code in the application:</p>
                <div style="background-color: #333333; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #FFD700; margin: 0;">{otp}</h2>
                </div>
                <p>The verification code will be valid for <strong>5 minutes</strong>. Please do not share this code with anyone.</p>
                <p style="margin-top: 20px;">Thank you,<br>The Binance Trading Team</p>
                <p style="text-align: center; margin-top: 40px; font-size: 12px; color: #555555;">Powered by Binance Trading</p>
            </div>
        </body>
        </html>
        """

        # Send the email
        send_mail(
            subject=subject,
            message="",  # Plain text fallback
            from_email=os.environ.get('EMAIL_USER'),
            recipient_list=[email],
            fail_silently=False,
            html_message=message,
        )

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class ResetPasswordAPI(APIView):

    @swagger_auto_schema(
        operation_description="Reset password using OTP",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
        ),
        responses={
            200: openapi.Response(description='Password reset successful'),
            400: openapi.Response(description='Invalid OTP'),
            404: openapi.Response(description='User with this email does not exist'),
        },
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        otp_obj = OTP.objects.get(email=user.email)

        if not otp_obj.verify(otp):
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
