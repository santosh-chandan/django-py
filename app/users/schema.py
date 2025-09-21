import graphene     # the GraphQL library for Python/Django.
from graphql import GraphQLError    # returning readable errors inside GraphQL instead of raw exceptions.

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import userProfile


# ----------------------
# Types
# ----------------------
# UserType is a GraphQL type (like a serializer in REST).
# Defines fields that can be queried: username, email, level.
class UserType(graphene.ObjectType):
    username = graphene.String()
    email = graphene.String()
    level = graphene.String()


# ----------------------
# Queries
# ----------------------
# Query is the root for all GraphQL queries.
# Defines a field me, which returns a UserType.
class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

#### When you make a GraphQL request, the Django request object is passed as info.context.

    # resolve_me = resolver function. Runs when you query { me { username ... } }.
    # info.context.user = current Django user (GraphQL injects request context).
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Not logged in")

        profile = getattr(user, "userprofile", None)

        return UserType(
            username=user.username,
            email=getattr(profile, "email", user.email),
            level=getattr(profile, "level", None)
        )



# LoginMutation defines a mutation for logging in.
# Arguments → input fields (like request body).
# Response has access and refresh tokens.
class LoginMutation(graphene.Mutation):
    class Arguments:                                # <--- defines what inputs GraphQL accepts
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    access = graphene.String()                      # <--- defines what fields the response will contain
    refresh = graphene.String()

    # mutate executes when client runs login.
    # Uses Django’s authenticate.
    # If user valid → generate JWT tokens (refresh + access).
    def mutate(self, info, username, password):     # <--- runs when client calls "login"
        from django.contrib.auth import authenticate

        user = authenticate(username=username, password=password)
        if not user:
            raise GraphQLError("Invalid credentials")

        refresh = RefreshToken.for_user(user)       # <--- SimpleJWT creates tokens
        return LoginMutation(
            access=str(refresh.access_token),       # <--- response fields populated
            refresh=str(refresh)
        )


class RefreshTokenMutation(graphene.Mutation):
    class Arguments:
        refresh = graphene.String(required=True)

    access = graphene.String()

    def mutate(self, info, refresh):
        try:
            token = RefreshToken(refresh)
            return RefreshTokenMutation(access=str(token.access_token))
        except Exception:
            raise GraphQLError("Invalid refresh token")


# ----------------------
# Mutations
# ----------------------
# Root Mutation class.
# Adds login and refresh_token as available mutations.
class Mutation(graphene.ObjectType):
    login = LoginMutation.Field()
    refresh_token = RefreshTokenMutation.Field()


# ----------------------
# Schema
# ----------------------
# Finally, builds GraphQL schema with Query and Mutation root objects.
schema = graphene.Schema(query=Query, mutation=Mutation)
