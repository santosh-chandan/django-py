import pytest
from app.posts.models import Post


# -----------------------
# 1) Test querying all posts (public, no auth required)
# -----------------------

# gql - Helper to call GraphQL queries/mutations using Django test client.
# client - django test client - built in fixturre
@pytest.mark.django_db
def test_post_query(client, gql, gql_user):

    # Create a sample post in DB
    post = Post.objects.create(title="Test Post", body="Hello World", author=gql_user)

    #  Uses gql fixture from conftest to send GraphQL query.
    query = """
        query {
            posts {
                id
                title
                body
                author {
                    username
                }
            }
        }
        """
    # Call gql helper (client, query)
    resp = gql(client, query)
    data = resp["data"]["posts"]

    # Assert the returned post matches DB
    assert len(data) == 1
    assert data[0]["title"] == post.title
    assert data[0]["author"]["username"] == gql_user.username


# -----------------------
# 2) Test querying single post by ID
# -----------------------
@pytest.mark.django_db
def test_post_query(client, gql, gql_user):
    post = Post.objects.create(title="Single Post", body="Content", author=gql_user)

    query = """
    query getPost($id: Int!) {
        post(id: $id) {
            id
            title
            body
        }
    }
    """
    variables = {"id": post.id}
    resp = gql(client, query, variables)
    data = resp["data"]["post"]

    assert data["title"] == post.title
    assert data["body"] == post.body


# -----------------------
# 3) Test creating a post (requires auth)
# -----------------------
@pytest.mark.django_db
def test_create_post(client, gql, gql_auth_headers):
    mutation = """
    mutation createPost($title: String!, $body: String!) {
        createPost(title: $title, body: $body) {
            id
            title
            body
            author {
                username
            }
        }
    }
    """
    variables = {"title": "New Post", "body": "GraphQL Mutation"}
    resp = gql(client, mutation, variables, headers=gql_auth_headers)
    data = resp["data"]["createPost"]

    assert data["title"] == "New Post"
    assert data["author"]["username"] == "santosh"
