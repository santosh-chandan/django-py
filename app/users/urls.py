from django.urls import path
from .views import UserMeView, MyTokenObtainPairView, MyTokenRefreshView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', MyTokenRefreshView.as_view(), name="token_refresh"),
    path('user/me/', UserMeView.as_view(), name='user_me')
]
