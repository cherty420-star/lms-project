from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def test_celery():
    """Тестовая задача для проверки работы Celery"""
    return "Celery is working!"


@shared_task
def send_course_update_notification(course_id, old_title, new_title, old_description, new_description):
    """Отправка уведомлений подписчикам об обновлении курса"""
    try:
        from .models import Course, Subscription

        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if not subscriptions.exists():
            return f"No subscribers for course: {course.title}"

        subject = f"Обновление курса: {course.title}"

        changes = []
        if old_title != new_title:
            changes.append(f"Название: '{old_title}' → '{new_title}'")
        if old_description != new_description:
            changes.append("Описание курса было обновлено")

        changes_text = "\n".join(f"- {change}" for change in changes) if changes else "- Были внесены обновления"

        message = f"""
Здравствуйте!

Курс "{course.title}" был обновлен.

Изменения:
{changes_text}

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
            return f"Sent to {len(recipient_list)} subscribers"

        return "No valid email addresses"

    except Exception as e:
        return f"Error: {str(e)}"