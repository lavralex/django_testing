import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(news_list, home_object_list):
    news_count = len(home_object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(news_list, home_object_list):
    first_news_date = home_object_list[0].date
    all_dates = [news.date for news in home_object_list]
    assert first_news_date == max(all_dates)


@pytest.mark.django_db
def test_comments_order(client, news, comment_list):
    response = client.get(
        reverse(
            'news:detail',
            args=(news.id,)
        )
    )
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_comments_list = [comment.created for comment in all_comments]
    comment_list = [comment.created for comment in comment_list]
    assert all_comments_list == comment_list


@pytest.mark.django_db
def test_form(authorized_client, news):
    response = authorized_client.get(reverse('news:detail', args=(news.id,)))
    assert isinstance(response.context['form'], CommentForm)
    authorized_client.logout()
    logout_response = authorized_client.get(
        reverse('news:detail', args=(news.id,))
    )
    assert 'form' not in logout_response.context
