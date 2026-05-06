from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='название')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='превью')
    description = models.TextField(verbose_name='описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True, related_name='courses', verbose_name='владелец')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    preview = models.ImageField(upload_to='lessons/', blank=True, null=True, verbose_name='превью')
    video_link = models.URLField(verbose_name='ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True, related_name='lessons', verbose_name='владелец')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='subscriptions', verbose_name='пользователь')
    course = models.ForeignKey('Course', on_delete=models.CASCADE,
                               related_name='subscriptions', verbose_name='курс')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Гарантируем уникальность пары

    def __str__(self):
        return f"{self.user.email} -> {self.course.title}"