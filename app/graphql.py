import strawberry
from app.users.schema import Query as UserQuery, Mutation as UserMutation
from app.posts.schema import Query as PostQuery, Mutation as PostMutation
from app.comments.schema import Query as CommentQuery, Mutation as CommentMutation


@strawberry.type
class Query(UserQuery, PostQuery, CommentQuery):
    pass

@strawberry.type
class Mutation(UserMutation, PostMutation, CommentMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
