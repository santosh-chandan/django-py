# app/users/schema.py
import strawberry
from typing import Optional
from strawberry.types import Info
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from graphql import GraphQLError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import userProfile


# -------------------------
# Strawberry Type for User
# -------------------------
@strawberry.type
class UserType:
    username: str
    email: str
    level: Optional[str]


# -------------------------
# Query
# -------------------------
@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: Info) -> UserType:
        """
        Return current logged-in user
        """
        # info.context.request.user gives the Django user
        user = info.context.request.user
        if user.is_anonymous:
            raise Exception("Not logged in")
        user: User = info.context.request.user
        if user.is_anonymous:
            raise GraphQLError("Not logged in")

        profile = getattr(user, "userprofile", None)
        return UserType(
            username=user.username,
            email=getattr(profile, "email", user.email),
            level=getattr(profile, "level", None)
        )

'''
mutation {
  login(username: "santa", password: "pass123") {
    access
    refresh
  }
}

'''

# -------------------------
# Mutations
# -------------------------
@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info: Info, username: str, password: str) -> "TokenType":
        """
        Login user and return access + refresh token
        """
        user = authenticate(username=username, password=password)
        if not user:
            raise GraphQLError("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return TokenType(
            access=str(refresh.access_token),
            refresh=str(refresh)
        )

    @strawberry.mutation
    def refresh_token(self, info: Info, refresh: str) -> str:
        """
        Return a new access token from a refresh token
        """
        try:
            user = info.context.request.user
            if user.is_anonymous:
                raise Exception("Not Logged in")
            token = RefreshToken(refresh)
            return str(token.access_token)
        except Exception:
            raise GraphQLError("Invalid refresh token")

'''
mutation {
  refreshToken(refresh: "<your-refresh-token>")
}

query {
  me {
    username
    email
    level
  }
}

'''
# -------------------------
# Token type for mutations
# -------------------------
@strawberry.type
class TokenType:
    access: str
    refresh: str


# -------------------------
# Finally, create the schema
# -------------------------
schema = strawberry.Schema(query=Query, mutation=Mutation)
