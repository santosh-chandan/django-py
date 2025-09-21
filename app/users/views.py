from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# the import just makes User available in Python, and the OneToOneField(User) connects your userProfile to User.
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from .models import userProfile
from .serializers import UserSerializer, LoginSerializer, RefreshSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer as JWTRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

'''
userProfile has a field user that links to Django's built-in User model.
Django automatically creates a reverse relation from the User object to the userProfile object.
By default, it uses the lowercase model name (userprofile) as the attribute.
So if you have a User instance user, you can access its profile with user.userprofile.
'''

# Create your views here.
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses = UserSerializer, tags=["Authentication"])
    def get(self, request):
        user = request.user
        try:
            profile = user.userprofile
        except userProfile.DoesNotExist:
            profile = None
        data = {
            'username': user.username,
            'email': profile.email if profile else user.email,
            'level': profile.level if profile else None
        }

        return Response(data)

@extend_schema(request=LoginSerializer,responses={200: TokenObtainPairSerializer}, tags=["Authentication"])
class MyTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(request=RefreshSerializer,responses={200: JWTRefreshSerializer}, tags=["Authentication"])
class MyTokenRefreshView(TokenRefreshView):
    pass
