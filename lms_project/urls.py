from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from lms.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView
from users.views import UserProfileViewSet, PaymentListView, UserRegistrationView, PaymentViewSet

# Настройка Schema View для документации
schema_view = get_schema_view(
    openapi.Info(
        title="LMS API Documentation",
        default_version='v1',
        description="Документация API для LMS системы",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@lms.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def api_root(request):
    return JsonResponse({
        "message": "LMS API Server",
        "documentation": {
            "swagger": "/swagger/",
            "redoc": "/redoc/",
        },
        "available_endpoints": {
            "auth": {
                "register": "/api/register/",
                "login": "/api/token/",
                "refresh": "/api/token/refresh/",
            },
            "admin_panel": "/admin/",
            "courses": "/api/courses/",
            "lessons": "/api/lessons/",
            "payments": "/api/payments/",
            "users": "/api/users/",
        },
    })


router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),

    # Документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # API endpoints
    path('api/', include(router.urls)),
    path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('api/lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)