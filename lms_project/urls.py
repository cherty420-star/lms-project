from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView


# Функция для корневого URL
def api_root(request):
    return JsonResponse({
        "message": "LMS API Server",
        "available_endpoints": {
            "admin_panel": "/admin/",
            "courses_list": "/api/courses/",
            "courses_detail": "/api/courses/{id}/",
            "lessons_list": "/api/lessons/",
            "lessons_detail": "/api/lessons/{id}/",
        },
        "documentation": "Используйте POST, GET, PUT, DELETE методы"
    })


# Настройка роутера для CourseViewSet
router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', api_root),  # Корневой путь - теперь будет работать
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('api/lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
]

# Для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)