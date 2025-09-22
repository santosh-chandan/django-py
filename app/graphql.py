import strawberry
from app.users.schema import schema as user_schema


@strawberry.type
class Query(user_schema.Query):
    pass

@strawberry.type
class Mutation(user_schema.Mutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
