from rest_framework import serializers
from .models import User, Payment
from lms.models import Course, Lesson


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default='')
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, default='')

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'payment_date', 'course', 'course_title',
                  'lesson', 'lesson_title', 'amount', 'payment_method']

