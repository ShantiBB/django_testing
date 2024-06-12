from django.contrib.auth import get_user_model
from django.test import TestCase
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

    def test_note_not_in_list_for_users(self):
        users = (
            (self.author, True),
            (self.another_author, False)
        )
        for user, access in users:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, access)

    def test_pages_contains_form(self):
        pages = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in pages:
            with self.subTest(page=page):
                self.client.force_login(self.author)
                response = self.client.get(reverse(page, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
