from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from .serializers import UserProfileSerializer, UserRegistrationSerializer

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Регистрация доступна всем

class UserRoleCheckView(APIView):
    def get(self, request):
        print(f"User: {request.user}, Role: {request.user.role}")
        return Response({"user": request.user.username, "role": request.user.role})
