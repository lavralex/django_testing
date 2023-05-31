from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)
        cls.not_author = User.objects.create(username='не автор')
        cls.auth_client_not_author = Client()
        cls.auth_client_not_author.force_login(cls.not_author)
        cls.client = Client()
        cls.note = Note.objects.create(
            title='заголовок',
            text='текст',
            slug='note_slug',
            author=cls.author
        )

    def test_routes(self):
        test_data = (
            (
                reverse('notes:home', None),
                self.client,
                HTTPStatus.OK
            ),
            (
                reverse('users:login', None),
                self.client,
                HTTPStatus.OK
            ),
            (
                reverse('users:logout', None),
                self.client,
                HTTPStatus.OK
            ),
            (
                reverse('users:signup', None), self.client, HTTPStatus.OK
            ),
            (
                reverse('notes:list', None),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:add', None),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:success', None),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:detail', args=(self.note.slug,)),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:edit', args=(self.note.slug,)),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:delete', args=(self.note.slug,)),
                self.auth_client_author,
                HTTPStatus.OK
            ),
            (
                reverse('notes:detail', args=(self.note.slug,)),
                self.auth_client_not_author,
                HTTPStatus.NOT_FOUND
            ),
            (
                reverse('notes:edit', args=(self.note.slug,)),
                self.auth_client_not_author,
                HTTPStatus.NOT_FOUND
            ),
            (
                reverse('notes:delete', args=(self.note.slug,)),
                self.auth_client_not_author,
                HTTPStatus.NOT_FOUND
            ),
        )
        for url, user, status in test_data:

            with self.subTest(url=url, user=user, status=status):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,))
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
