from rest_framework import viewsets
from .models import User
from .serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для редактирования профиля пользователя"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer