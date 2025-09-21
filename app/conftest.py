# conftest.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from graphene_django.utils.testing import graphql_query
from app.users.models import userProfile

# -----------------------
# Fixtures for REST
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
        # Create userProfile for extra fields
        userProfile.objects.create(user=user, email=user.email, level='beginner')
    return user

@pytest.fixture
def auth_client(api_client, user1):
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client

# -----------------------
# Fixtures for GraphQL
# -----------------------

@pytest.fixture
def gql_user(db):
    """GraphQL test user with profile."""
    user = User.objects.create_user(
        username="santosh",
        password="testpass",
        email="santosh@example.com"
    )
    userProfile.objects.create(user=user, email=user.email, level="beginner")
    return user

@pytest.fixture
def gql_get_tokens(client, gql_user):
    """
    Logs in via GraphQL mutation and returns {"access": "...", "refresh": "..."}.
    """
    query = """
    mutation Login($username: String!, $password: String!) {
      login(username: $username, password: $password) {
        access
        refresh
      }
    }
    """
    variables = {"username": gql_user.username, "password": "testpass"}

    resp = graphql_query(query, variables=variables, client=client)
    content = resp.json()
    if "errors" in content:
        raise AssertionError(f"GraphQL login failed: {content['errors']}")

    return content["data"]["login"]

@pytest.fixture
def gql_auth_headers(gql_get_tokens):
    """Authorization headers for GraphQL requests (Bearer <token>)."""
    tokens = gql_get_tokens
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}
