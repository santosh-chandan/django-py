'''

Serializer = acts like a "bridge" between Django models and JSON APIs.
Converts complex data (like Django models or querysets) into Python primitives (dicts, lists) that can then be easily converted to JSON for APIs.
Validates incoming data when a client (frontend, mobile app, etc.) sends data to your API.
Creates or updates model instances from validated data.

'''

from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'user', 'user_username','is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'body', 'is_published']
