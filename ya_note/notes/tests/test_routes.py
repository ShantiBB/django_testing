from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.not_author = User.objects.create_user(
            username='another_author', password='password'
        )
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author,
            slug='pytest_trial-note'
        )

    def test_availability_for_anonymous_user(self):
        pages = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for page, args in pages:
            with self.subTest():
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_note_for_users(self):
        pages = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        users = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND)
        )
        for user, status in users:
            for page, args in pages:
                with self.subTest():
                    self.client.force_login(user)
                    url = reverse(page, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability_for_auth_user(self):
        pages = ('notes:list', 'notes:add', 'notes:success')
        for page in pages:
            with self.subTest():
                self.client.force_login(self.not_author)
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        pages = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for page, args in pages:
            url = reverse(page, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
