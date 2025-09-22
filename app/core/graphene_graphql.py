# app/posts/schema.py
import graphene
from graphene_django.types import DjangoObjectType
from ..posts.models import Post
from graphql import GraphQLError

# -------------------------
# GraphQL Type for Post
# -------------------------
# class PostType(graphene.ObjectType):
    # need to add every field with data type like id = graphene.Int() 
    # if use DjangoObjectType then it map from django model directly
    # Type is kind of serializer
class PostType(DjangoObjectType):
    """
    Converts Django model 'Post' into a GraphQL type.
    Fields like id, title, body, author, created_at are automatically exposed.
    """
    class Meta:
        model = Post
        fields = ("id", "title", "body", "author", "created_at", "updated_at")


class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id=graphene.Int(required=True))

    def resolve_posts(self, info):
        return Post.objects.all().order_by("-created_at")
    
    def resolve_post(self, info, id):
        # user = info.context.user
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")
'''
query {
  posts {
    id
    title
    body
    author {
      username
    }
  }
}

query {
  post(id: 3) {
    id
    title
    body
    author {
      username
    }
  }
}

'''

# -------------------------
# Query Multiple Parameters
# -------------------------
'''
class Query(graphene.ObjectType):
    # GraphQL field "post" takes two arguments: id and title
    post = graphene.Field(
        PostType,
        id=graphene.Int(required=True),
        title=graphene.String(required=True)
    )

    # Resolver: gets called when you query { post(id: 1, title: "Hello") { ... } }
    def resolve_post(self, info, id, title):
        try:
            return Post.objects.get(id=id, title=title)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")
        
# If title is not mandatory
class Query(graphene.ObjectType):
    # here only id is required, title is optional
    post = graphene.Field(
        PostType,
        id=graphene.Int(required=True),
        title=graphene.String()   # 👈 optional, no required=True
    )

    def resolve_post(self, info, id, title=None):   # 👈 default None
        try:
            if title:
                # both id + title filter
                return Post.objects.get(id=id, title=title)
            else:
                # only id filter
                return Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

query {
  post(id: 1, title: "Hello World") {
    id
    title
    body
  }
}

'''
# -------------------------
# Create Post
# -------------------------
class CreatePostMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        body = graphene.String(required=True)

    post = graphene.Field(PostType)  # The post object to return after creation

    def mutate(self, info, title, body):
        user = info.context.user  # Django user from request
        if user.is_anonymous:
            raise GraphQLError("Not logged in")

        post = Post.objects.create(title=title, body=body, author=user)
        return CreatePostMutation(post=post)

# -------------------------
# Update Post
# -------------------------
class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        body = graphene.String()

    post = graphene.Field(PostType)     # return type

    def mutate(self, info, id, title=None, body=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Not logged in")
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        if post.author != user:
            raise GraphQLError("Not allowed to edit this post")

        if title:
            post.title = title
        if body:
            post.body = body
        post.save()
        # this is the heart of how Python scoping works inside classes.
        # post in the class is a schema field.
        # post in the function is a local variable.
        # Python reads this as:
            # post= → keyword argument name, must match a class field.
            # post (right-hand side) → local variable, your ORM object.
        return UpdatePostMutation(post=post)

# -------------------------
# Delete Post
# -------------------------
class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()  # Returns True if deletion successful

    def mutate(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Not logged in")
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        if post.author != user:
            raise GraphQLError("Not allowed to delete this post")

        post.delete()
        return DeletePostMutation(ok=True)

# Root mutation
class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()

# create_post is the field name in Python schema.
# By default, Graphene will convert snake_case → camelCase in the GraphQL schema.
# So create_post (Python) automatically becomes createPost (GraphQL).

'''
mutation {
  createPost(title: "GraphQL Post", body: "Hello world!") {
    post {
      id
      title
      body
    }
  }
}

mutation {
  updatePost(id: 1, title: "Updated title") {
    post {
      id
      title
      body
    }
  }
}

mutation {
  deletePost(id: 1) {
    ok
  }
}
'''

# Final schema
schema = graphene.Schema(query=Query, mutation=Mutation)
