from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from .models import User, Payment
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PaymentSerializer,
    UserProfileWithPaymentsSerializer, PaymentCreateSerializer,
    PaymentRetrieveSerializer
)
from .permissions import IsOwner, IsModerator
from lms.models import Course


class IsNotModerator(permissions.BasePermission):
    """Разрешение для пользователей, которые не являются модераторами"""

    def has_permission(self, request, view):
        return not IsModerator().has_permission(request, view)


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
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def payments_history(self, request, pk=None):
        """История платежей пользователя"""
        user = self.get_object()
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


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentRetrieveSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Создание платежа и получение ссылки на оплату"""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data.get('course').id
        course = get_object_or_404(Course, id=course_id)
        amount = float(serializer.validated_data.get('amount'))

        # Здесь будет интеграция со Stripe
        # Пока возвращаем заглушку
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            payment_method='card',
            status='pending',
            payment_url=f"https://checkout.stripe.com/pay/test_{course.id}"
        )

        return Response({
            "payment_id": payment.id,
            "payment_url": payment.payment_url,
            "message": "Перейдите по ссылке для оплаты курса (тестовый режим)"
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='(?P<course_id>[^/.]+)/success')
    def payment_success(self, request, course_id=None):
        """Обработка успешной оплаты"""
        course = get_object_or_404(Course, id=course_id)
        payment = Payment.objects.filter(
            user=request.user,
            course=course,
            status='pending'
        ).order_by('-payment_date').first()

        if payment:
            payment.status = 'paid'
            payment.save()
            return Response({
                "message": f"Оплата курса '{course.title}' успешно завершена!",
                "course_id": course.id,
                "amount": payment.amount
            })

        return Response({
            "message": f"Курс '{course.title}' оплачен. Спасибо за покупку!"
        })

    @action(detail=False, methods=['get'], url_path='(?P<course_id>[^/.]+)/cancel')
    def payment_cancel(self, request, course_id=None):
        """Обработка отмены оплаты"""
        course = get_object_or_404(Course, id=course_id)
        return Response({
            "message": f"Оплата курса '{course.title}' была отменена",
            "course_id": course.id
        })

    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        """Проверка статуса платежа"""
        payment = self.get_object()
        return Response({
            "payment_id": payment.id,
            "status": payment.status,
            "amount": payment.amount,
            "course": payment.course.title if payment.course else None
        })