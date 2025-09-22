
# conftest.py
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from app.users.models import userProfile
import json

# -----------------------
# REST API fixtures
# -----------------------
@pytest.fixture
def api_client():
    return APIClient()

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
        userProfile.objects.create(user=user, email=user.email, level='beginner')
    return user

@pytest.fixture
def auth_client(api_client, user1):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user1)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client

# -----------------------
# GraphQL fixtures
# -----------------------

@pytest.fixture
def gql():
    """
    Helper to call GraphQL queries/mutations using Django test client.
    Usage:
        resp = gql(client, query, variables, headers)
    """
    def _gql(client, query, variables=None, headers=None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        resp = client.post(
            "/graphql",
            data=json.dumps(payload),
            content_type="application/json",
            **(headers or {})
        )
        return resp.json()
    return _gql

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
    resp = client.post(
        "/graphql",
        data={"query": query, "variables": variables},
        content_type="application/json"
    )
    content = resp.json()
    if "errors" in content:
        raise AssertionError(f"GraphQL login failed: {content['errors']}")
    return content["data"]["login"]

@pytest.fixture
def gql_auth_headers(gql_get_tokens):
    """Authorization headers for GraphQL requests (Bearer <token>)."""
    tokens = gql_get_tokens
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}
