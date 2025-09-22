from strawberry.django.views import GraphQLView
from app.services.middleware import JWTMiddleware
from app.services.schema import schema

class AuthGraphQLView(GraphQLView):
    def __init__(self, **kwargs):
        super().__init__(schema=schema, middleware=[JWTMiddleware()], **kwargs)
    schema = schema
    middleware = [JWTMiddleware()]
