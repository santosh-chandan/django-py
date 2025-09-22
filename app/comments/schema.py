import strawberry
import strawberry_django
from typing import List, Optional
from strawberry.types import Info
from django.contrib.auth.models import User
from .models import Comment

# Comment Type
@strawberry_django.type(Comment)
class commentType:        # ❌ Should use PascalCase by convention
    id : strawberry.auto
    author: strawberry.auto
    post: strawberry.auto
    content: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def comments(self, info:Info) -> List[commentType]:
        try:
            return Comment.objects.all().order_by("-created_at")
        except Exception:
            return None
    
    @strawberry.field
    def comment(self, info:Info, id:int) -> Optional[commentType]:
        try:
            return Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_comment(self, info: Info, post_id: int, content: str ) -> commentType:
        try:
            user = info.context.request.user
            if user.is_anonymous:
                raise Exception("user not loagged in")
            comment = Comment.objects.create(post_id=post_id, author=user, content=content)
            return comment
        except Exception:
            return None

    @strawberry.mutation
    def update_comment(self, info:Info, id: int, post_id: Optional[int] = None, content: Optional[str] = None) -> commentType:
        try:
            user = info.context.request.user
            if user.is_anonymous:
                raise Exception("user not logged in")
            comment = Comment.objects.get(id=id)
            if comment.author != user:
                raise Exception("Not allowed to edit this comment")
            comment.content = content
            comment.save()
            return comment
        except Exception:
            return None
    
    @strawberry.mutation
    def delete_comment(self, info: Info, id:int) -> bool:
        user = info.context.request.user
        if user.is_anonymous:
                raise Exception("user not logged in")
        try:
           comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            raise Exception("Post not found")
        comment.delete()
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)
