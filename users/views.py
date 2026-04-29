from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PaymentSerializer,
    UserProfileWithPaymentsSerializer
)
from .permissions import IsOwner, IsModerator


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для управления профилями пользователей"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        elif self.action == 'retrieve':
            # Для просмотра чужого профиля - ограниченная информация
            if self.get_object() != self.request.user:
                return UserProfileSerializer
        return UserProfileSerializer

    def get_permissions(self):
        # Для просмотра профиля - только аутентификация
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        # Для обновления и удаления - проверка владельца
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def payments_history(self, request, pk=None):
        """История платежей пользователя"""
        user = self.get_object()
        # Проверяем, что пользователь просматривает свой профиль
        if user != request.user and not IsModerator().has_permission(request, self):
            return Response(
                {"error": "Доступ запрещен. Вы можете просматривать только свои платежи."},
                status=status.HTTP_403_FORBIDDEN
            )
        payments = user.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaymentListView(generics.ListAPIView):
    """Список платежей с фильтрацией"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = PaymentPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    permission_classes = [permissions.IsAuthenticated]