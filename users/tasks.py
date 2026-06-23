from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    # Вычисляем дату месяц назад
    month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, которые не заходили более месяца
    inactive_users = User.objects.filter(
        Q(last_login__lt=month_ago) | Q(last_login__isnull=True),
        is_active=True,
        is_superuser=False  # Не блокируем суперпользователей
    )

    # Подсчитываем количество
    count = inactive_users.count()

    # Блокируем пользователей (обновляем одним запросом)
    updated_count = inactive_users.update(is_active=False)

    # Логируем результат
    result = f"Blocked {updated_count} inactive users (total found: {count})"
    print(result)

    return result


@shared_task
def send_welcome_email(user_id):
    """
    Отправка приветственного письма новому пользователю
    """
    try:
        user = User.objects.get(id=user_id)
        subject = "Добро пожаловать в LMS систему!"
        message = f"""
        Здравствуйте, {user.first_name or user.email}!

        Спасибо за регистрацию в нашей LMS системе.

        Теперь вы можете:
        - Проходить курсы
        - Получать уведомления об обновлениях
        - Следить за своим прогрессом

        С уважением,
        Команда LMS
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return f"User {user_id} does not exist"