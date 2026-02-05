from django.test import TestCase
from django.contrib.auth.models import User
from ...models import Post, Comment
from django.utils import timezone
from datetime import timedelta

class CommentModelTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username='commenter', password='123')
        # create test post
        self.post = Post.objects.create(
            author=self.user,
            title="Base post",
            text_content="This is the base post",
            image="http://example.com/image.jpg"
        )

    def test_creating_comment(self):
        """Verify correct creation and linking to post of a comment"""
        comment = Comment.objects.create(
            parent_post=self.post,
            author=self.user,
            text_content="This is a Comment!"
        )
        self.assertEqual(comment.text_content, "This is a Comment!")
        self.assertEqual(comment.parent_post.title, "Base post")
        self.assertEqual(comment.author.username, "commenter")
        self.assertEqual(self.post.comments.first(), comment)
        self.assertEqual(self.post.comments.count(), 1)

    def test_comment_str_method(self):
        """Test if the __str__ method returns the correct values"""
        comment = Comment.objects.create(
            parent_post=self.post,
            author=self.user,
            text_content="This is a Comment!"
        )
        self.assertIn("This is a Comment!", str(comment))

    def test_timestamp_working(self):
        """Verify if timestamps are generated correctly"""
        comment = Comment.objects.create(
            parent_post=self.post,
            author=self.user,
            text_content="Checking time..."
        )
        self.assertIsNotNone(comment.timestamp)

        now = timezone.now()

        self.assertAlmostEqual(
            comment.timestamp, 
            now, 
            delta=timedelta(seconds=10) # Using a tighter delta
        )
