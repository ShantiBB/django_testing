from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.another_author = User.objects.create_user(
            username='another_author', password='password'
        )
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='test-note',
            author=cls.author
        )
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.client_another_author = Client()
        cls.client_another_author.force_login(cls.another_author)

    def test_note_not_in_list_for_users(self):
        users = (
            (self.client_author, True),
            (self.client_another_author, False)
        )
        for user, access in users:
            with self.subTest(user=user):
                response = user.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, access)

    def test_pages_contains_form(self):
        pages = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in pages:
            with self.subTest(page=page):
                response = self.client_author.get(
                    reverse(page, args=args)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
