from rest_framework import serializers
from .models import User, Payment
from lms.models import Course, Lesson


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password_confirm', 'first_name',
                  'last_name', 'phone', 'city', 'avatar']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'city', 'avatar']


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'amount', 'payment_method', 'course', 'lesson']


class UserProfileWithPaymentsSerializer(serializers.ModelSerializer):
    payments = PaymentHistorySerializer(many=True, read_only=True)
    total_payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone', 'city', 'avatar', 'payments', 'total_payments']

    def get_total_payments(self, obj):
        return obj.payments.aggregate(total=models.Sum('amount'))['total'] or 0


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, default='')
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, default='')

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'payment_date', 'course', 'course_title',
                  'lesson', 'lesson_title', 'amount', 'payment_method']