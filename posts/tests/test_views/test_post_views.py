from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ...models import Post

class PostListTests(APITestCase):
    def setUp(self):
        self.url = reverse('post-list')
        self.user = User.objects.create_user(
            username='author',
            password='secure_password123',
        )
        self.first_post = Post.objects.create(
            title="Some Post",
            text_content="Hello world!",
            author=self.user
        )
        self.second_post = Post.objects.create(
            title="Some Other Post",
            text_content="Hello to the world!",
            author=self.user
        )

    ### VALID
    def test_see_posts_as_guest(self):
        """Confirms that users who are not logged in are able to see posts"""

        # makes sure we are logged out
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the returned data should contain both our posts
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Some Post')

    def test_create_post_authenticated_user(self):
        """Confirms that a logged-in user can successfully create a post"""
        # force_authenticate skips checking credentials and pretends this user is already logged in
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Test Post",
            "text_content": "A" * 15,  # reach min. lenght
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Test Post")

        # get the freshly created post and compare the author to our logged in user
        new_post = Post.objects.get(title="Test Post")
        self.assertEqual(new_post.author, self.user)

    ### INVALID
    def test_create_post_unauthenticated_user(self):
        """Confirms that a guest cannot create a post"""
        self.client.logout()
        data = {
            "title": "Guest Post",
            "content": "A" * 15
        }

        response = self.client.post(self.url, data, format='json')

        # should be 403 Forbidden because of IsAuthenticatedOrReadOnly
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verify the post was not created
        self.assertFalse(Post.objects.filter(title="Guest Post").exists())

    def test_create_post_invalid_data(self):
        """Confirms that the posts with missing data aren't created"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": ""
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostDetailTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='secure_password123'
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            password='secure_password123'
        )
        self.post = Post.objects.create(
            title="Owner's Post",
            text_content="This post's author is the owner",
            author=self.owner
        )
        self.url = reverse('post-detail', kwargs={'pk': self.post.pk})
        
    ### VALID
    
    
    ### INVALID