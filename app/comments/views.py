from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import CommentCreateSerializer, CommentListSerializer, CommentUpdateSerializer
from .models import Comment
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import AutoSchema


class CommentListView(APIView):
    schema = AutoSchema()

    # GET /api/comments/
    @extend_schema(responses=CommentListSerializer, description="List Comments", tags=["Comments"])
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data)

    # POST /api/comments/
    @extend_schema(request=CommentCreateSerializer, responses=CommentCreateSerializer, description="Create Comment", tags=["Comments"])
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    schema = AutoSchema()
    serializer_class = CommentUpdateSerializer  # helps schema generation
    
    @extend_schema(request=CommentUpdateSerializer, responses=CommentUpdateSerializer, description="Update Comment", tags=["Comments"])
    def put(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Delete Comment", tags=["Comments"])
    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
'''
# partial=True
    Now DRF allows only some fields to be updated.
    Fields not provided in request.data will stay unchanged.
    This is usually what PATCH implies — partial update.
'''
