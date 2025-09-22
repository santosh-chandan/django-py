
import pytest 
from app.comments.models import Comment
from app.posts.models import Post

# what ever pass in parameter will call automatically first
@pytest.fixture
def post1(db, user1):
    return Post.objects.create(title="Hello", body="World", user=user1, is_published=True)

# understand flow - if call comment1 will call and pass post1 in param so first post1 will call auto as pass in param
@pytest.fixture
def comment1(db, post1, user1):
    return Comment.objects.create(author=user1, post=post1, content="First comment!")


# ---------------
# Testcase
# ---------------
@pytest.mark.django_db
class TestCommentAPI:
    def test_list_comments(self, auth_client, comment1):
        resp = auth_client.get('/api/comments/')
        assert resp.status_code == 200

    def test_create_comment(self, auth_client, user1, post1):
        data = {"post":post1.id, "content": "Hello Comment"}
        resp = auth_client.post('/api/comments/', data, format="json")
        assert resp.status_code == 201
        assert resp.data["content"] == "Hello Comment"
        assert Comment.objects.filter(post=post1, author=user1).count() == 1

    def test_update_comment(self, auth_client, comment1):
        data = {"content": "updated Comment"}
        resp = auth_client.put(f'/api/comments/{comment1.id}/', data, format="json")
        assert resp.status_code == 204
        comment1.refresh_from_db()
        assert comment1.content == "updated Comment"

    def test_delete_comment(self, auth_client, comment1):
        resp = auth_client.delete(f'/api/comments/{comment1.id}/')
        assert resp.status_code == 200
        assert not comment1.object.filter(id = comment1.id).exist()

# def test_create_comment_unauthenticated(self, api_client, post1):
#         """Anonymous users cannot create comments (expect 401)."""
#         data = {"post": post1.id, "content": "Should fail"}
#         resp = api_client.post("/api/comments/", data, format="json")
#         assert resp.status_code in (401, 403)
