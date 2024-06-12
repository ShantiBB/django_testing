from datetime import timedelta, datetime
import pytest

from django.test.client import Client
from django.utils import timezone
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create_user(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Title', text='Text')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        author=author, news=news, text='Comment Text'
    )


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def count_news_on_home_page(news):
    today = datetime.today()
    return News.objects.bulk_create([News(
        title=f'Новость {i}',
        text='Просто текст.',
        date=today - timedelta(days=i)
    ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ])


@pytest.fixture
def count_comments_on_news(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data(news, author):
    return {'text': 'New comment text'}
