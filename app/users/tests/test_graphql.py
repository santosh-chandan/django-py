# tests/test_graphql_auth.py
import pytest
import json
from django.urls import reverse
from app.users.models import userProfile
from django.contrib.auth.models import User

# -------------------------------
# Helper function to send GraphQL requests via Django test client
# -------------------------------
def gql(client, query, variables=None, headers=None):
    """
    Send a POST request to the Strawberry GraphQL endpoint.
    """
    body = {"query": query}
    if variables:
        body["variables"] = variables

    headers = headers or {}
    response = client.post(
        reverse("graphql"),  # Strawberry URL name
        data=json.dumps(body),
        content_type="application/json",
        **headers
    )
    return response

# -------------------------------
# 1) Test login mutation
# -------------------------------
@pytest.mark.django_db
def test_login_mutation(client, gql_user):
    query = """
    mutation Login($username: String!, $password: String!) {
      login(username: $username, password: $password) {
        access
        refresh
      }
    }
    """
    variables = {"username": gql_user.username, "password": "testpass"}

    resp = gql(client, query, variables)
    content = resp.json()

    assert "errors" not in content
    tokens = content["data"]["login"]
    assert tokens.get("access")
    assert tokens.get("refresh")

# -------------------------------
# 2) Test refresh token mutation
# -------------------------------
@pytest.mark.django_db
def test_refresh_token_mutation(client, gql_get_tokens):
    tokens = gql_get_tokens  # fixture returns {"access": "...", "refresh": "..."}

    query = """
    mutation RefreshToken($refresh: String!) {
      refreshToken(refresh: $refresh) {
        access
      }
    }
    """
    variables = {"refresh": tokens["refresh"]}

    resp = gql(client, query, variables)
    content = resp.json()

    assert "errors" not in content
    assert content["data"]["refreshToken"]["access"]

# -------------------------------
# 3) Test me query with authentication
# -------------------------------
@pytest.mark.django_db
def test_me_query_authenticated(client, gql_user, gql_auth_headers):
    query = """
    query {
      me {
        username
        email
        level
      }
    }
    """
    resp = gql(client, query, headers=gql_auth_headers)
    content = resp.json()

    assert "errors" not in content
    me = content["data"]["me"]
    assert me["username"] == gql_user.username
    assert me["email"] == gql_user.email
    assert me["level"] == "beginner"

# -------------------------------
# 4) Test me query as anonymous user
# -------------------------------
@pytest.mark.django_db
def test_me_query_anonymous(client):
    query = """
    query {
      me {
        username
      }
    }
    """
    resp = gql(client, query)
    content = resp.json()

    # Resolver should raise Exception("Not logged in")
    assert "errors" in content
    assert content["errors"][0]["message"] == "Not logged in"
