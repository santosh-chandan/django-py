import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from app.users.models import userProfile

# -----------------------
# Fixtures
# -----------------------

"""Unauthenticated DRF client."""
@pytest.fixture
def api_client():
    return APIClient()

"""Default test user (santa)."""
@pytest.fixture
def user1(db):
    return User.objects.create_user(username='santa', password='pass123')

@pytest.fixture
def user2(db):
    return User.objects.create_user(username='banta', password='pass234')

@pytest.fixture
def user3(db):
    user, created = User.objects.get_or_create(
        username='santa',
        defaults={'email': 'santa@example.com'}
    )
    if created:
        user.set_password('pass123')
        user.save()
        # Create userProfile
        userProfile.objects.create(user=user, email=user.email, level='beginner')
    return user

@pytest.fixture
def auth_client(api_client, user1):
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client
