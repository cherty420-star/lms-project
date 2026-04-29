from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsOwner, IsModerator, CanEditCourseOrLesson, IsOwnerOrReadOnlyForModerator


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для Course с правами доступа"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            # Создание и удаление только для владельцев (не модераторов)
            self.permission_classes = [permissions.IsAuthenticated,
                                       lambda: not IsModerator().has_permission(self.request, self)]
        elif self.action in ['update', 'partial_update']:
            # Обновление: модераторы могут, владельцы могут
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            # Просмотр списка: все аутентифицированные
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'retrieve':
            # Просмотр деталей: все аутентифицированные
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Автоматически назначаем владельца
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        # Модераторы видят все курсы
        if IsModerator().has_permission(self.request, self):
            return Course.objects.all()
        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


class LessonListCreateView(generics.ListCreateAPIView):
    """GET список уроков и POST создание урока"""
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание только для владельцев (не модераторов)
            return [permissions.IsAuthenticated(),
                    lambda: not IsModerator().has_permission(self.request, self)]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Модераторы видят все уроки
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        # Автоматически назначаем владельца
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE для конкретного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Удаление только для владельцев
            return [permissions.IsAuthenticated(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Обновление: модераторы могут, владельцы могут
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)