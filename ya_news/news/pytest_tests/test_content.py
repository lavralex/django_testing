import pytest
from django.conf import settings
from django.urls import reverse


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
def test_comments_order(client, news_with_comments):
    response = client.get(
        reverse(
            'news:detail',
            args=(news_with_comments.id,)
        )
    )
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(authorized_client, news):
    response = authorized_client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' in response.context
