from rest_framework import serializers
from .models import Comment

class CommentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id','post','author','content','created_at']
        read_only_fields = ['id','author']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id','post','author','content','created_at']
        read_only_fields = ['id','author']

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id','author','post','content','created_at']
        read_only_fields = ['id','author']
