import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def authorized_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def authorized_reader(client, reader):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
    )


@pytest.fixture
def news_list():
    news_list = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news, author=author, text='комментарий'
    )


@pytest.fixture
def news_with_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timezone.timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def news_id_arg(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {"text": "комментарий", }


@pytest.fixture
def home_object_list(client):
    response = client.get(reverse('news:home'))
    return response.context['object_list']


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", kwargs={"pk": comment.pk})
