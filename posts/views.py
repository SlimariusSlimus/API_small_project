from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from posts.models import Post, Comment
from posts.serializers import PostSerializer, CommentSerializer, RegistrationSerializer
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class PostList(APIView):
    """
    List all posts or create a new post instance

    Methods:
        GET:        Retrieve a list of all existing posts                                             Accessible by any user (Authenticated or Guest)
        POST:       Create a new post, automatically assigning the logged-in user as the author       Restricted to Authenticated users
    """
    # ensures that only logged-in users can POST (GET requests will still be handed to the guest user)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    def get(self, request):
        """Return a list of all posts"""
        posts = Post.objects.all()
        # serialization: (object -> json)
        serializer = PostSerializer(posts, many=True)
        # return the json data to the user
        return Response(serializer.data)

    def post(self, request):
        """Create a new post with the provided data and authenticated user"""
        # deserialization: (json -> object)
        serializer = PostSerializer(data=request.data)

        # validation check for model requirements
        # if validation fails DRF stops here and sends a 400 Bad Request back to the user (so we don't have to use any if logic)
        serializer.is_valid(raise_exception=True)

        # the json doesn't include the autor, so we 'inject' the logged-in user here
        # this ensures the post is linked to the right person safely and automatically
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetail(APIView):
    # this handles if the user is logged in AND if they own the post
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # try to find the specific post and check ownership
    def _get_object(self, pk):
        """Helper method to find the post and check permissions"""
        post = get_object_or_404(Post, pk=pk)
        # this triggers the IsOwnerOrReadOnly check
        self.check_object_permissions(self.request, post)
        return post

    # retrieve the specific post
    def get(self, request, pk):
        post = self._get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # replace the entire post with new data
    def put(self, request, pk):
        post = self._get_object(pk)
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # update only specific fields
    def patch(self, request, pk):
        post = self._get_object(pk)
        # partial=True allows missing fields in the request
        serializer = PostSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # remove the post from the database
    def delete(self, request, pk):
        post = self._get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentList(APIView):
    """
    List all comments for a specific post or create a new comment

    Methods:
        GET:        Retrieve a list of all comments linked to a specific post    Accessible by any user (Authenticated or Guest)
        POST:       Create a new comment for a post, assigning the logged-in
                    user as the author and linking the post automatically        Restricted to Authenticated users
    """
    # ensures that only logged-in users can POST (GET requests will still be handed to the guest user)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    def get(self, request, post_pk):
        """
        Return a list of all comments belonging to a specific post

        Args:
            post_pk (int): The primary key of the parent post
        """
        # verify if the post exists
        post = get_object_or_404(Post, pk=post_pk)
        comments = Comment.objects.filter(parent_post=post)
        # serialization: (object -> json)
        serializer = CommentSerializer(comments, many=True)
        # return the json data to the user
        return Response(serializer.data)

    def post(self, request, post_pk):
        """
        Create a new comment for a specific post with the provided data

        Args:
            post_pk (int): The primary key of the post being commented on
        """
        post = get_object_or_404(Post, pk=post_pk)
        # deserialization: (json -> object)
        serializer = CommentSerializer(data=request.data)

        # validation check for model requirements
        serializer.is_valid(raise_exception=True)

        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentDetail(APIView):
    """
    Update or delete a specific comment instance (only allowed for the author/owner)

    Methods:
        PATCH:      Update specific fields of a comment (e.g., the text)
        DELETE:     Remove the comment from the database
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def _get_object(self, pk):
        """Helper method to find the post and check permissions"""
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(self.request, comment)
        return comment

    def patch(self, request, pk):
        """
        Update specific fields of a comment by ID

        Args:
            pk (int):   The primary key of the comment to update
        """
        comment = self._get_object(pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Permanently delete a specific comment by ID

        Args:
            pk (int):   The primary key of the comment to remove
        """
        comment = self._get_object(pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthenticationLogin(APIView):
    """
    Authenticate a user and return a unique token

    Methods:
        POST:       Validate credentials and return a new API token (replaces any existing token)
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # ensures only one active session by removing the user's previous token before creating a new one
            tokens = Token.objects.filter(user=user)
            if tokens:
                tokens[0].delete()
            token = Token.objects.create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):
    """
    Register a new user account and return an initial token

    Methods:
        POST:       Create a new user instance and automatically generate an authentication token
    """
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            # create a token for the new user
            token = Token.objects.create(user=user)
            return Response({"user": serializer.data, "token": token.key}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
