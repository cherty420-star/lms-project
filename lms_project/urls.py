from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView
from users.views import UserProfileViewSet, PaymentListView


def api_root(request):
    return JsonResponse({
        "message": "LMS API Server",
        "available_endpoints": {
            "admin_panel": "/admin/",
            "courses_list": "/api/courses/",
            "courses_detail": "/api/courses/{id}/",
            "lessons_list": "/api/lessons/",
            "lessons_detail": "/api/lessons/{id}/",
            "payments_list": "/api/payments/",
            "users": "/api/users/",
        },
        "filters_for_payments": {
            "course": "/api/payments/?course=1",
            "lesson": "/api/payments/?lesson=1",
            "payment_method": "/api/payments/?payment_method=cash",
            "ordering": "/api/payments/?ordering=payment_date",
            "reverse_ordering": "/api/payments/?ordering=-payment_date",
        }
    })


router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'users', UserProfileViewSet)

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('api/lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('api/payments/', PaymentListView.as_view(), name='payment-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)