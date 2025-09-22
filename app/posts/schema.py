# app/posts/schema.py
import strawberry
import strawberry_django
from typing import List, Optional
from strawberry.types import Info
from django.contrib.auth.models import User
from .models import Post

# -------------------------
# Strawberry Type for Post
# -------------------------
# @strawberry.type will not convert defined atrribute into django model post
# means we need to defin type of all attrinute int or char
@strawberry_django.type(Post)
class PostType:
    id: strawberry.auto
    title: strawberry.auto
    body: strawberry.auto
    user: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


# -------------------------
# Query
# -------------------------
@strawberry.type
class Query:
    @strawberry.field
    def posts(self, info: Info) -> List[PostType]:
        """Return all posts"""
        return Post.objects.all().order_by("-created_at")

    @strawberry.field
    def post(self, info: Info, id: int) -> Optional[PostType]:      # means the function can return either a PostType or None.
        """Return single post by ID"""
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

'''
query {
  posts {
    id
    title
    body
    user {
      username
    }
  }
}

query {
  post(id: 1) {
    id
    title
    body
  }
}

'''

# -------------------------
# Mutations
# -------------------------
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_post(self, info: Info, title: str, body: str) -> PostType:
        """Create a new post"""
        user: User = info.context.request.user
        if user.is_anonymous:
            raise Exception("Not logged in")

        post = Post.objects.create(title=title, body=body, user=user)
        return post


    @strawberry.mutation
    def update_post(
        self, info: Info, id: int, title: Optional[str] = None, body: Optional[str] = None
    ) -> PostType:
        """Update a post by ID"""
        user: User = info.context.request.user
        if user.is_anonymous:
            raise Exception("Not logged in")

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise Exception("Post not found")

        if post.user != user:
            raise Exception("Not allowed to edit this post")

        if title:
            post.title = title
        if body:
            post.body = body
        post.save()
        return post

    @strawberry.mutation
    def delete_post(self, info: Info, id: int) -> bool:
        """Delete a post by ID"""
        user: User = info.context.request.user
        if user.is_anonymous:
            raise Exception("Not logged in")

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise Exception("Post not found")

        if post.user != user:
            raise Exception("Not allowed to delete this post")

        post.delete()
        return True

# create_post is the field name in Python schema.
# By default, Graphene will convert snake_case → camelCase in the GraphQL schema.
# So create_post (Python) automatically becomes createPost (GraphQL).

'''
mutation {
  createPost(title: "First Post", body: "Hello Strawberry!") {
    id
    title
    body
    author {
      id
      username
    }
  }
}

mutation {
  updatePost(id: 1, title: "Updated Title") {
    id
    title
    body
  }
}

mutation {
  deletePost(id: 1)
}

'''

# -------------------------
# Schema
# -------------------------
schema = strawberry.Schema(query=Query, mutation=Mutation)
