from django.test import TestCase
from django.contrib.auth.models import User
from ...models import Post
from django.utils import timezone
from datetime import timedelta

class PostModelTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username='poster', password='123')
        # create test post
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            text_content="This is a test",
            image="http://example.com/image.jpg"
        )

    def test_creating_post(self):
        """Verify correct creation of a post and linking the author user"""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.author.username, "poster")

    def test_post_str_method(self):
        """Test if the __str__ method returns the correct values"""
        self.assertIn("Test Post", str(self.post))

    def test_timestamp_working(self):
        """Verify if timestamps are generated correctly"""
        self.assertIsNotNone(self.post.timestamp)
        now = timezone.now()
        self.assertAlmostEqual(
            self.post.timestamp, 
            now, 
            delta=timedelta(minutes=1)
        )
