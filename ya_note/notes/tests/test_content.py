from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')
    NUMBER_OF_NOTES = 3
    FIRST_SLUG = 0

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.user = User.objects.create(username='другой пользователь')
        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Запись {index}',
                text='Просто текст.',
                slug=f'{index}',
                author=cls.author
            )
            for index in range(cls.FIRST_SLUG, cls.NUMBER_OF_NOTES)
        )

    def test_note_in_list(self):
        users = (
            (self.author, list(Note.objects.all())),
            (self.user, []),
        )
        for user, expected_notes in users:
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            notes = list(response.context['object_list'])
            self.assertEqual(notes, expected_notes)

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.FIRST_SLUG,)),
        )
        for name, args in urls:
            self.client.force_login(self.author)
            response = self.client.get(reverse(name, args=args))
            self.assertIn('form', response.context)
