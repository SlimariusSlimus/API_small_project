from django.urls import path
from . import views

urlpatterns = [
    ### Auth Endpoints
    path('auth/', views.AuthenticationLogin.as_view(), name='auth-login'),
    path('register/', views.Register.as_view(), name='register'),

    ### Post Endpoints
    # list all posts or create a new one
    path('posts/', views.PostList.as_view(), name='post-list'),
    # retrieve, update, or delete a specific post
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post-detail'),

    ### Comment Endpoints
    # list comments for a specific post or add a new comment to it
    path('posts/<int:post_pk>/comments/', views.CommentList.as_view(), name='comment-list'),
    # update or delete a specific comment by its  ID
    path('comments/<int:pk>/', views.CommentDetail.as_view(), name='comment-detail'),
]
