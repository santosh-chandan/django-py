from django.urls import path
from .views import CommentListView, CommentDetailView

urlpatterns = [
    path('comments/', CommentListView.as_view(), name="comment-list-create"),
    path('comments/<int:pk>', CommentDetailView.as_view(), name="comment-detail")
]
