from django.test import TestCase
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from .models import Course, Lesson, Subscription


class LessonTests(APITestCase):

    def setUp(self):
        # Создаем пользователей
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='test123',
            first_name='Owner'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='test123',
            first_name='Other'
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='test123',
            first_name='Moderator'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс и урок
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.owner
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner
        )

        # Настраиваем клиенты
        self.client = APIClient()

    def test_create_lesson_valid_youtube_link(self):
        """Тест создания урока с валидной youtube ссылкой"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'Description',
            'video_link': 'https://www.youtube.com/watch?v=valid',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_invalid_link(self):
        """Тест создания урока с невалидной ссылкой (не youtube)"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'Description',
            'video_link': 'https://www.rutube.ru/video/test',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Title')

    def test_update_lesson_not_owner(self):
        """Тест обновления урока не владельцем"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        # Не владелец не видит чужой урок
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator(self):
        """Тест удаления урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        # Модератор может удалять? По заданию - нет
        # Если запрещено - 403 или 404
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_list_lessons_owner(self):
        """Тест получения списка уроков владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_lessons_moderator(self):
        """Тест получения списка уроков модератором (видит все)"""
        # Создаем урок другого пользователя
        Lesson.objects.create(
            title='Other Lesson',
            description='Other Description',
            video_link='https://www.youtube.com/watch?v=other',
            course=self.course,
            owner=self.other_user
        )

        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class SubscriptionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Description',
            owner=self.user
        )

        self.client = APIClient()

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-subscribe', args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_double_subscribe(self):
        """Тест повторной подписки (должна быть ошибка)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-subscribe', args=[self.course.id])
        # Первая подписка
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Вторая подписка (должна быть ошибка)
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-subscribe', args=[self.course.id])

        # Сначала подписываемся
        self.client.post(url)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Затем отписываемся
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_not_subscribed(self):
        """Тест отписки без подписки (должна быть ошибка)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-subscribe', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_subscribed_field(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-detail', args=[self.course.id])

        # Проверяем без подписки
        response = self.client.get(url)
        self.assertFalse(response.data['is_subscribed'])

        # Подписываемся
        subscribe_url = reverse('course-subscribe', args=[self.course.id])
        self.client.post(subscribe_url)

        # Проверяем с подпиской
        response = self.client.get(url)
        self.assertTrue(response.data['is_subscribed'])