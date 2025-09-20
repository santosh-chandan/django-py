from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.schemas import AutoSchema
from .serializers import PostSerializer, PostCreateUpdateSerializer
from .models import Post
from .utils import IsOwnerOrReadOnly

from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import AutoSchema

@extend_schema(tags=["Blogs"])
class PostViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Post model using only default DRF components.
    """
    queryset = Post.objects.select_related('user').all()
    # get_serializer_class() might return None then use this serializer_class
    serializer_class = PostSerializer  # DRF uses it whenever get_serializer_class() is not overridden.
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    throttle_scope = 'user'  # use DRF's default throttles
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_published'] # , 'user__username'
    search_fields = ['title', 'body']
    ordering_fields = ['created_at', 'updated_at']
    schema = AutoSchema() # per-view schema generator used to build API documentation (OpenAPI/Swagger).

    # Overriding get_serializer_class
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PostCreateUpdateSerializer
        return PostSerializer

    def get_queryset(self):
        """
        Optionally filter by query params:
        - ?mine=true => only posts of request.user (if authenticated)
        """
        qs = super().get_queryset()
        mine = self.request.query_params.get('mine')
        if mine and self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        # Set user automatically
        serializer.save(user=self.request.user)


    # What @action(detail=True) means
    # detail=True → this action applies to a single object (so it requires the {id} in the URL).
    # DRF appends your action's name (publish) after the object path. So it becomes: - /api/posts/{id}/publish/
    # Example of a custom action
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def publish(self, request, pk=None):
        try:
            post = self.get_object()
            if not request.user.is_staff:
                return Response(status=403)
        except Post.DoesNotExist:
            raise NotFound(detail="Post not found")

        post.is_published = True
        post.save(update_fields=['is_published'])
        return Response({'status': 'published'}, status=status.HTTP_200_OK)
    # detail=False → URL: /api/posts/publish/ (collection-level action, you must handle id manually).
