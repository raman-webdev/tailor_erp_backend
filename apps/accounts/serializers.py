from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)


    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )

    
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        
        return attrs
    
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)

        return user
    

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
            "is_verified",
            "created_at",
        )
        read_only_fields = fields


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "profile_picture",
        )

    def validate_profile_picture(self, image):
        if image is None:
            return image

        if image.size > 15 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image must be less than 5 MB."
            )

        allowed = [
            "image/jpeg",
            "image/png",
            "image/webp",
        ]

        if image.content_type not in allowed:
            raise serializers.ValidationError(
                "Only JPG, PNG and WEBP images are allowed."
            )

        return image


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                "confirm_password": "Passwords do not match."
                }
            )
        validate_password(attrs["new_password"])

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )

        return attrs
    

class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()



