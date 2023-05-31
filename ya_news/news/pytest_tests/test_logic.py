from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0
    comment = Comment.objects.filter(text=form_data['text']).first()
    assert comment is None


@pytest.mark.django_db
def test_user_can_create_comment(
    authorized_client,
    news, author,
    detail_url,
    form_data
):
    response = authorized_client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(authorized_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = authorized_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context_data['form'].errors == {'text': [WARNING]}
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'user, status, comment_objects_count',
    (
        (pytest.lazy_fixture('authorized_client'), HTTPStatus.FOUND, 0),
        (pytest.lazy_fixture('authorized_reader'), HTTPStatus.NOT_FOUND, 1),
    )
)
@pytest.mark.django_db
def test_delete_comment(
    user,
    status,
    comment_objects_count,
    delete_url
):
    response = user.delete(delete_url)
    assert response.status_code == status
    comments_count = Comment.objects.count()
    assert comments_count == comment_objects_count


def test_author_can_edit_comment(
    authorized_client,
    comment,
    form_data,
    edit_url,
    detail_url
):
    response = authorized_client.post(edit_url, data=form_data)
    assert response.url == f'{detail_url}#comments'
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    authorized_reader,
    comment,
    form_data,
    edit_url,
):
    response = authorized_reader.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
