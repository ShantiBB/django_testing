from http import HTTPStatus

import pytest
from django.urls import reverse

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id, form_data
):
    news_url = reverse('news:detail', args=news_id)
    assert Comment.objects.count() == 0
    client.post(news_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client, author, news, news_id, form_data
):
    assert Comment.objects.count() == 0
    news_url = reverse('news:detail', args=news_id)
    author_client.post(news_url, data=form_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client, news_id):
    news_url = reverse('news:detail', args=news_id)
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response, form='form', field='text', errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, comment, comment_id, news_id
):
    news_url = reverse('news:detail', args=news_id)
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=comment_id)
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author,
        news,
        author_client,
        comment,
        comment_id,
        news_id,
        form_data
):
    news_url = reverse('news:detail', args=news_id)
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=comment_id)
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == form_data['text']


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment, comment_id, news_id
):
    delete_url = reverse('news:delete', args=comment_id)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_comment_of_another_user(
    author,
    news,
    not_author_client,
    comment,
    comment_id,
    form_data
):
    edit_url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.author == author
    assert comment.news == news
    assert comment.text != form_data['text']
