from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Для курсов и уроков проверяем поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Для пользователей
        return obj == request.user


class CanEditCourseOrLesson(permissions.BasePermission):
    """
    Модераторы могут просматривать и редактировать, но не создавать/удалять.
    Владельцы могут делать всё со своими объектами.
    """

    def has_permission(self, request, view):
        # Для создания (POST) - только владельцы
        if view.action == 'create':
            return request.user.is_authenticated and not IsModerator().has_permission(request, view)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модераторы могут просматривать, обновлять (но не удалять)
        if IsModerator().has_permission(request, view):
            # Модераторы не могут удалять
            if view.action == 'destroy':
                return False
            # Модераторы могут просматривать и обновлять любые объекты
            return True

        # Владельцы могут делать всё со своими объектами
        return obj.owner == request.user


class IsOwnerOrReadOnlyForModerator(permissions.BasePermission):
    """
    Модераторы могут просматривать любые объекты, но не редактировать и не удалять.
    Владельцы могут просматривать, редактировать и удалять свои объекты.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем просмотр всем аутентифицированным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Модераторы не могут редактировать и удалять
        if IsModerator().has_permission(request, view):
            return False

        # Владельцы могут редактировать и удалять
        return obj.owner == request.user