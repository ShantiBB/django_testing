from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

from notes.forms import WARNING
from pytils.translit import slugify

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.another_author = User.objects.create_user(
            username='another_author', password='password'
        )
        cls.form = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
            'author': cls.author
        }
        cls.add_url = reverse('notes:add')

    def test_user_can_create_note(self):
        self.assertEqual(Note.objects.count(), 0)
        self.client.force_login(self.author)
        response = self.client.post(self.add_url, data=self.form)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form['title'])
        self.assertEqual(note.text, self.form['text'])
        self.assertEqual(note.slug, self.form['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        self.assertEqual(Note.objects.count(), 0)
        response = self.client.post(self.add_url, data=self.form)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        self.client.force_login(self.author)
        note = Note.objects.create(**self.form)
        self.form['slug'] = note.slug
        response = self.client.post(self.add_url, data=self.form)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.client.force_login(self.author)
        self.form.pop('slug')
        response = self.client.post(self.add_url, data=self.form)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditAndDeleteNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.not_author = User.objects.create_user(
            username='another_author', password='password'
        )
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='test-note',
            author=cls.author
        )
        cls.form = {
            'title': 'New title',
            'text': 'New text',
            'slug': 'new-slug',
            'author': cls.author
        }

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form['title'])
        self.assertEqual(self.note.text, self.form['text'])
        self.assertEqual(self.note.slug, self.form['slug'])

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.not_author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.client.force_login(self.not_author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
