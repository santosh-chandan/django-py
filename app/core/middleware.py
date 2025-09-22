# app/core/middleware.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

class JWTMiddleware:
    """
    Strawberry middleware to attach user to request based on JWT token.
    """

    def resolve(self, next_, root, info, **kwargs):
        request = info.context.request  # Django HttpRequest

        # Default user is anonymous
        request.user = getattr(request, "user", AnonymousUser())

        # Look for Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            auth = JWTAuthentication()
            try:
                # the expiration is inside the JWT itself, not in the database.
                # {
                # "user_id": 1,
                # "token_type": "access",
                # "exp": 1700000000,
                # "iat": 1699996400
                # }
                user_auth_tuple = auth.get_validated_token(token)
                user = auth.get_user(user_auth_tuple)
                request.user = user
            except Exception:
                # Invalid token, leave as anonymous
                request.user = AnonymousUser()

        # Continue to next resolver
        return next_(root, info, **kwargs)
