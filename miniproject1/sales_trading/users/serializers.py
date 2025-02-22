from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'role', 'avatar')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'avatar')