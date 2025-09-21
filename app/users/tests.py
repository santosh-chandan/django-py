# app/users/tests.py
import pytest
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from app.users.models import userProfile



# -----------------------
# Tests
# -----------------------
@pytest.mark.django_db
class TestUserAPI:
    def test_user_login(self, auth_client, user1):
        data = {"username": user1.username, "password": "pass123"}
        resp = auth_client.post("/api/login/", data, format="json")
        assert resp.status_code == 200
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_user_me(self, auth_client, user3):
        resp = auth_client.get("/api/user/me/")
        assert resp.status_code == 200
        assert resp.data["username"] == user3.username

    def test_token_refresh(self, auth_client, user1):
        # login first to get refresh token
        login_data = {"username": user1.username, "password": "pass123"}
        login_resp = auth_client.post("/api/login/", login_data, format="json")
        refresh_token = login_resp.data['refresh']

        resp = auth_client.post(f"/api/token/refresh/", {"refresh": refresh_token}, format="json")
        assert resp.status_code == 200
        assert 'access' in resp.data
