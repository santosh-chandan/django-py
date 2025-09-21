import graphene
from app.users.schema import schema as user_schema


# It acts as a base class fallback in case none of the inherited queries include it.
# Even if all sub-queries already inherit from graphene.ObjectType, including it again at the end is safe and explicit.
class Query(user_schema.Query, graphene.ObjectType):
    # This merges queries from all apps
    pass
# we could remove graphene.ObjectType and still work
class Mutation(user_schema.Mutation, graphene.ObjectType):
    # This merges mutations from all apps
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
