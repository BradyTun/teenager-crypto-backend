from .models import User
from rest_framework import serializers
import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs.get("email"))
        except User.DoesNotExist:
            raise AuthenticationFailed("No active account found with the given credentials")

        if not user.check_password(attrs.get("password")):
            raise AuthenticationFailed("Your password is incorrect")

        return super().validate(attrs)

class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    referred_user_id = serializers.CharField(required=False)  # Accept referred user ID or email
    country = serializers.CharField(required=True)

    def create(self, validated_data):
        # Get the referred user if provided
        referred_user = None
        if "referred_user_id" in validated_data:
            try:
                referred_user = User.objects.get(id=int(validated_data["referred_user_id"].replace('XRPCC', '')))
            except User.DoesNotExist:
                raise serializers.ValidationError({"referred_user_id": "Invalid invitation code"})

        # Create the user
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            referred_user=referred_user,
            country=validated_data["country"],
        )
        return user

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['photo', 'date_of_birth', 'username']
        extra_kwargs = {
            'photo': {'required': False},
            'date_of_birth': {'required': False},
            'username': {'required': False},
        }

    def validate_username(self, value):
        return value
