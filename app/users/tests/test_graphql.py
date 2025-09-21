# Tests for the GraphQL auth schema: login, refresh_token, and me query.
import pytest
from graphene_django.utils.testing import graphql_query


'''
pytest-django ships with some default fixtures:
client → Django test client (django.test.Client)

from django.test import Client
@pytest.fixture
def client():
    """Custom Django test client if you want to override default one."""
    return Client()

'''

# -------------------------------
# 1) Test the login mutation
# -------------------------------
@pytest.mark.django_db  # mark this test needs DB access
def test_login_mutation(client, gql_user):
    # GraphQL mutation to call the LoginMutation defined in your schema
    query = """
    mutation {
      login(username: $username, password: $password) {
        access
        refresh
      }
    }
    """

    # variables for the mutation: match credentials of the `user` fixture
    variables = {"username": gql_user.username, "password": "testpass"}

    # send the request using graphql_query helper and the Django test client
    resp = graphql_query(query, variables=variables, client=client)
    content = resp.json()                # parse the JSON body

    assert "errors" not in content       # ensure GraphQL returned no errors
    tokens = content["data"]["login"]    # access the returned data.login
    # check both tokens are present and non-empty
    assert tokens.get("access")
    assert tokens.get("refresh")

# -------------------------------
# 2) Test refresh_token mutation
# -------------------------------
@pytest.mark.django_db
def test_refresh_token_mutation(client, gql_get_tokens):
    # get_tokens is a fixture that returns a callable which logs in and returns tokens
    tokens = gql_get_tokens()                # {"access": "...", "refresh": "..."}

    # GraphQL mutation to exchange a refresh token for a new access token
    # # Operation name = RefreshToken so you can remove RefreshToken($refresh: String!)
    query = """
    mutation RefreshToken($refresh: String!) {
      refreshToken(refresh: $refresh) {
        access
      }
    }
    """

    variables = {"refresh": tokens["refresh"]}   # pass the refresh token

    resp = graphql_query(query, variables=variables, client=client)
    content = resp.json()

    assert "errors" not in content               # ensure no GraphQL errors
    # assert the returned access token exists
    assert content["data"]["refreshToken"]["access"]


# -------------------------------
# 3) Test me query as authenticated user
# -------------------------------
@pytest.mark.django_db
def test_me_query_authenticated(client, auth_headers, user):
    # GraphQL query to read current user details (your resolve_me uses info.context.user)
    query = """
    query {
      me {
        username
        email
        level
      }
    }
    """

    # pass Authorization header via headers param (Django test client expects HTTP_AUTHORIZATION)
    resp = graphql_query(query, client=client, headers=auth_headers)
    content = resp.json()

    assert "errors" not in content               # ensure no GraphQL errors
    me = content["data"]["me"]                   # the returned user object
    # verify returned values match the user created in fixture
    assert me["username"] == user.username
    assert me["email"] == user.email
    # level comes from userProfile if present; your fixture didn't create profile, so expect None
    assert me["level"] is None

# -------------------------------
# 4) Test me query as anonymous user (should fail)
# -------------------------------
@pytest.mark.django_db
def test_me_query_anonymous(client):
    # same query but no auth header provided
    query = """
    query {
      me {
        username
      }
    }
    """
    resp = graphql_query(query, client=client)
    content = resp.json()

    # resolver raises GraphQLError("Not logged in") — GraphQL returns this as an error
    assert "errors" in content
    assert content["errors"][0]["message"] == "Not logged in"
