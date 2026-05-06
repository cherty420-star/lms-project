from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from .paginators import CoursePaginator, LessonPaginator
from users.permissions import IsModerator, IsOwner


class IsNotModerator(permissions.BasePermission):
    """Разрешение для пользователей, которые не являются модераторами"""

    def has_permission(self, request, view):
        return not IsModerator().has_permission(request, view)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для Course с правами доступа"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_permissions(self):
        if self.action == 'create':
            # Создание только для обычных пользователей (не модераторов)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        elif self.action == 'destroy':
            # Удаление только для владельцев
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Обновление для всех аутентифицированных (проверка в has_object_permission)
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'subscribe':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        """
        POST: Подписаться на курс
        DELETE: Отписаться от курса
        """
        course = self.get_object()
        subscription = Subscription.objects.filter(user=request.user, course=course)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {"error": "Вы уже подписаны на этот курс"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=request.user, course=course)
            return Response(
                {"message": "Вы успешно подписались на обновления курса"},
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {"error": "Вы не подписаны на этот курс"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(
                {"message": "Вы отписались от обновлений курса"},
                status=status.HTTP_204_NO_CONTENT
            )


class LessonListCreateView(generics.ListCreateAPIView):
    """GET список уроков и POST создание урока"""
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание только для обычных пользователей (не модераторов)
            return [permissions.IsAuthenticated(), IsNotModerator()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE для конкретного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Модераторы могут редактировать любые уроки
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)