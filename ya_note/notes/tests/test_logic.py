from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='автор')
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)
        cls.user = User.objects.create(username='пользователь')
        cls.auth_client_user = Client()
        cls.auth_client_user.force_login(cls.user)
        cls.note = Note.objects.create(
            title='заголовок',
            text='текст',
            slug='slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'заголовок записи',
            'text': 'Текст записи',
            'slug': 'note_slug'
        }
        cls.form_data_duplicate_slug = {
            'title': 'Заголовок записи',
            'text': 'Текст записи',
            'slug': cls.form_data['slug']
        }

    def test_anonymous_user_cant_create_note(self):
        start_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, start_count)

    def test_user_can_create_note(self):
        start_count = Note.objects.count()
        self.auth_client_author.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, start_count + 1)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_user_cant_duplicate_slug(self):
        self.auth_client_author.post(self.url, data=self.form_data)
        start_count = Note.objects.count()
        response = self.auth_client_author.post(
            self.url,
            data=self.form_data_duplicate_slug
        )
        slug = self.form_data['slug']
        self.assertFormError(response, 'form', 'slug', f'{slug}{WARNING}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, start_count)

    def test_empty_slug(self):
        start_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.auth_client_author.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), start_count + 1)
        new_note = Note.objects.get(slug=slugify(self.form_data['title']))
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client_author.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client_user.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_other_user_cant_delete_note(self):
        start_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client_user.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), start_count)

    def test_author_can_delete_note(self):
        start_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client_author.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), start_count - 1)
