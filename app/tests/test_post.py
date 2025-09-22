# app/post/tests/test_post_api.py
import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from ..posts.models import Post

User = get_user_model()


# -----------------------
# Fixtures (reusable setup)
# -----------------------
@pytest.fixture
def api_client():
    """A plain DRF APIClient (not authenticated)."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user 'alice' in the test database."""
    return User.objects.create_user(username='alice', password='pass1234')


@pytest.fixture
def user2(db):
    """Create a second test user 'bob'."""
    return User.objects.create_user(username='bob', password='pass1234')


@pytest.fixture
def auth_client(api_client, user, db):
    """
    Return an APIClient that is authenticated as `user` (alice).
    We create a Token and attach it to the client's Authorization header.
    """
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def post1(db, user):
    """Create a simple Post owned by `user` (alice)."""
    return Post.objects.create(title='Hello', body='World', user=user, is_published=False)


# -----------------------
# Test class
# -----------------------
@pytest.mark.django_db
class TestPostAPI:
    """Grouped API tests for Post endpoints."""

    def test_list_posts(self, auth_client, post1):
        """Authenticated user can list posts (expects paginated response)."""
        resp = auth_client.get('/api/posts/')
        assert resp.status_code == 200
        assert 'results' in resp.data  # PageNumberPagination wraps results in "results"

    def test_create_post(self, auth_client, user):
        """Authenticated user can create a post; user should be set to the authenticated user."""
        data = {'title': 'New', 'body': 'Body of post', 'is_published': True}
        resp = auth_client.post('/api/posts/', data, format='json')
        assert resp.status_code == 201
        # one existing post (post1) + new one = 2
        #assert Post.objects.filter(user=user).count() == 2
        # verify the post returned has correct user
        assert resp.data['user'] == user.id

    def test_update_not_user(self, api_client, user2, post1):
        """
        A non-user (bob) trying to update alice's post should be denied.
        Some APIs return 403 Forbidden, others 404 Not Found to hide existence — accept either.
        """
        token2 = Token.objects.create(user=user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')
        resp = api_client.put(
            f'/api/posts/{post1.id}/',
            {'title': 'X', 'body': 'Y', 'is_published': False}
        )
        assert resp.status_code in (403, 404)

    def test_publish_action_admin_only(self, auth_client, post1):
        """Custom action /publish/ should be admin-only; non-admin should get 403."""
        resp = auth_client.post(f'/api/posts/{post1.id}/publish/')
        assert resp.status_code == 403
