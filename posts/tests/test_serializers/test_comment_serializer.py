from django.test import TestCase
from django.contrib.auth.models import User
from ...serializers import CommentSerializer
from ...models import Post, Comment
from rest_framework.exceptions import ValidationError

class CommentSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='some_password'
        )

        self.parent_post = Post.objects.create(
            author=self.user,
            title='Valid Title',
            text_content='This is a post with enough length.',
            image='https://example.com/image.png'
        )

    ### Field tests
    ## VALID
    def test_valid_text_content(self):
        """Validates that text content within length constraints (15-4000) does not raise an error"""
        field = CommentSerializer().fields['text_content']
        # min_lenght = 15; max_lenght = 4000
        valid_text_content = 'This is a valid comment'

        try:
            field.run_validators(valid_text_content)
        except ValidationError:
            self.fail("unexpected ValidationError!")
            
    ## INVALID
    def test_text_content_length_too_short(self):
        """Tests if a ValidationError is raised when the text_content is below the 15 character minimum"""
        field = CommentSerializer().fields['text_content']
        # min_length is 15
        too_short_text_content = 'too short'

        with self.assertRaises(ValidationError):
            field.run_validators(too_short_text_content)

    def test_text_content_length_too_long(self):
        """Tests if a ValidationError is raised when the title is above the 4000 character maximum"""
        field = CommentSerializer().fields['text_content']
        # max_length is 200
        too_long_text_content = 'A' * 4001

        with self.assertRaises(ValidationError):
            # max_length is 200
            field.run_validators(too_long_text_content)


    ### Profanity
    ## non-profane content is covered through the previous tests

    def test_text_content_profanity_integration_profane_content(self):
        """Verifies the text_content field correctly throws a ValidationError when profane language is used"""
        field = CommentSerializer().fields['text_content']
        profane_text_content = 'Fuck this profanity filter!'

        with self.assertRaises(ValidationError):
            field.run_validators(profane_text_content)


    ### Sanitization & Representation
    ## Sanitization (deserialization)
    def test_internal_value_sanitization(self):
        """Checks that HTML tags and whitespaces are stripped from input data during the deserialization (to_internal_value)"""
        unclean_text_content = {
            'parent_post': self.parent_post.id,
            'text_content': '   <p>This is a long enough post to get through the checks.</p>'
        }
        serializer = CommentSerializer(data=unclean_text_content)

        # is.valid() calls the to_internal_value method of the serializer
        # adding ", serializer.errors" inside the assertTrue also prints the error message to the console
        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(serializer.validated_data['text_content'], 'This is a long enough post to get through the checks.')

