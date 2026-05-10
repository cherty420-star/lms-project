from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id, old_title, new_title, old_description, new_description):
    """
    Отправка уведомлений подписчикам об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if not subscriptions.exists():
            return f"No subscribers for course: {course.title}"

        # Формируем письмо
        subject = f"Обновление курса: {course.title}"

        # Определяем, что именно изменилось
        changes = []
        if old_title != new_title:
            changes.append(f"Название: '{old_title}' → '{new_title}'")
        if old_description != new_description:
            changes.append("Описание курса было обновлено")

        changes_text = "\n".join(
            f"- {change}" for change in changes) if changes else "- Были внесены обновления в материалы курса"

        message = f"""
Здравствуйте!

Курс "{course.title}" был обновлен.

Изменения:
{changes_text}

Перейдите в курс, чтобы ознакомиться с обновлениями.

С уважением,
Команда LMS
        """

        # Собираем список email получателей
        recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Sent notifications to {len(recipient_list)} subscribers for course: {course.title}"

        return f"No valid email addresses for course: {course.title}"

    except Course.DoesNotExist:
        return f"Course {course_id} does not exist"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"


@shared_task
def send_lesson_update_notification(lesson_id, course_id, lesson_title, old_content, new_content):
    """
    Отправка уведомлений подписчикам об обновлении урока (дополнительное задание)
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if not subscriptions.exists():
            return f"No subscribers for course: {course.title}"

        subject = f"Обновление урока в курсе: {lesson_title}"

        message = f"""
Здравствуйте!

Урок "{lesson_title}" в курсе "{course.title}" был обновлен.

Изменения затронули содержание урока.

Перейдите в курс, чтобы ознакомиться с обновлениями.

С уважением,
Команда LMS
        """

        recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Sent notifications to {len(recipient_list)} subscribers for lesson: {lesson_title}"

        return f"No valid email addresses for lesson: {lesson_title}"

    except Course.DoesNotExist:
        return f"Course {course_id} does not exist"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"


@shared_task
def test_celery():
    """
    Тестовая задача для проверки работы Celery
    """
    return "Celery is working!"