from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.user = User.objects.create(username='другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_note_in_list(self):
        users = (
            (self.author, self.assertIn),
            (self.user, self.assertNotIn),
        )
        for user, check in users:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                notes = response.context['object_list']
                check(self.note, notes)

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            self.client.force_login(self.author)
            response = self.client.get(reverse(name, args=args))
            self.assertIsInstance(response.context['form'], NoteForm)
