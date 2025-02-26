from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer

User = get_user_model()

# class CustomUserCreateSerializer(UserCreateSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'username', 'password', 'role', 'avatar')
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'role', 'avatar')

    def create(self, validated_data):
        """Создаём пользователя с хешированным паролем"""
        password = validated_data.pop('password')  # Извлекаем пароль
        user = User(**validated_data)  # Создаём объект без сохранения
        user.set_password(password)  # Хешируем пароль
        user.save()  # Сохраняем пользователя
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'avatar')