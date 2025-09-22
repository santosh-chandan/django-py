"""
URL configuration for multiplex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.shortcuts import redirect
# from graphene_django.views import GraphQLView
from app.services.graphql import AuthGraphQLView
from django.views.decorators.csrf import csrf_exempt

def redirect_to_swagger(request):
    return redirect('/api/docs/swagger/')

urlpatterns = [
    # path('', home),  # root URL
    path('', redirect_to_swagger),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('app.posts.urls')),
    path('api/', include('app.comments.urls')),
    path('api/', include('app.users.urls')),   # 👈 add this line

    # OpenAPI schema/docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Global GraphQL endpoint
    # csrf_exempt is needed because GraphQL POST requests often come without CSRF tokens (especially from external clients).
    # graphiql=True enables the GraphiQL playground UI at /graphql/ so you can test queries interactively.
    path("graphql/", csrf_exempt(AuthGraphQLView.as_view())),
]
