from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fill database with sample payment data'

    def handle(self, *args, **options):
        # Создаем тестовые данные если их нет
        if not Course.objects.exists():
            course1 = Course.objects.create(
                title="Python Basics",
                description="Learn Python from scratch"
            )
            course2 = Course.objects.create(
                title="Django Framework",
                description="Master Django"
            )

            Lesson.objects.create(
                title="Lesson 1",
                description="Introduction",
                video_link="https://youtu.be/example1",
                course=course1
            )
            Lesson.objects.create(
                title="Lesson 2",
                description="Advanced",
                video_link="https://youtu.be/example2",
                course=course1
            )

        # Создаем тестовых пользователей если их нет
        if not User.objects.filter(email='test@test.com').exists():
            user1 = User.objects.create_user(
                email='test@test.com',
                password='test123',
                phone='+123456789',
                city='Moscow'
            )
            user2 = User.objects.create_user(
                email='ivan@example.com',
                password='ivan123',
                phone='+987654321',
                city='Saint Petersburg'
            )

        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())
        users = list(User.objects.all())

        # Создаем платежи
        payment_methods = ['cash', 'transfer']

        for i in range(20):
            user = random.choice(users)
            amount = Decimal(random.randint(500, 5000)) / 100
            payment_method = random.choice(payment_methods)
            payment_date = datetime.now() - timedelta(days=random.randint(0, 365))

            # Случайно выбираем курс или урок
            payment_type = random.choice(['course', 'lesson'])

            if payment_type == 'course' and courses:
                course = random.choice(courses)
                Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    course=course,
                    amount=amount,
                    payment_method=payment_method
                )
            elif lessons:
                lesson = random.choice(lessons)
                Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    lesson=lesson,
                    amount=amount,
                    payment_method=payment_method
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully created payments!'))