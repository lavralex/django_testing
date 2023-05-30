from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_arg',)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_availability(client, news, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('authorized_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('authorized_reader'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(
    client,
    user,
    status,
    comment
):
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    (
        'news:edit',
        'news:delete'
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
