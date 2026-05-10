from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_link', 'course', 'owner', 'updated_at']
        read_only_fields = ['owner', 'updated_at']

    def validate_video_link(self, value):
        return validate_youtube_url(value)

    def update(self, instance, validated_data):
        from django.utils import timezone
        from datetime import timedelta

        # Сохраняем старые значения
        old_title = instance.title
        old_description = instance.description

        # Обновляем instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Проверяем, прошло ли более 4 часов с последнего обновления
        if instance.updated_at and instance.updated_at < timezone.now() - timedelta(hours=4):
            if old_title != instance.title or old_description != instance.description:
                from .tasks import send_lesson_update_notification
                send_lesson_update_notification.delay(
                    instance.id,
                    instance.course.id,
                    instance.title,
                    old_description,
                    instance.description
                )

        return instance


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'owner',
                  'lessons_count', 'lessons', 'is_subscribed', 'updated_at']
        read_only_fields = ['owner', 'updated_at']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    def update(self, instance, validated_data):
        # Сохраняем старые значения для отправки уведомлений
        old_title = instance.title
        old_description = instance.description

        # Обновляем instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Отправляем уведомление, если были изменения
        if old_title != instance.title or old_description != instance.description:
            from .tasks import send_course_update_notification
            send_course_update_notification.delay(
                instance.id,
                old_title,
                instance.title,
                old_description,
                instance.description
            )

        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_email', 'course', 'course_title', 'created_at']
        read_only_fields = ['user', 'created_at']