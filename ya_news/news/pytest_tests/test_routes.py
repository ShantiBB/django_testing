from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

NEWS_EDIT_AND_DELETE = ('news:edit', 'news:delete')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page',
    NEWS_EDIT_AND_DELETE
)
def test_comment_redirect_for_anonymous_client(
        client, comment_id, page
):
    login_url = reverse('users:login')
    url = reverse(page, args=comment_id)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'page',
    NEWS_EDIT_AND_DELETE
)
@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_availability_for_comment_edit_and_delete(
        user, status, page, comment_id
):
    url = reverse(page, args=comment_id)
    response = user.get(url)
    assert response.status_code == status
