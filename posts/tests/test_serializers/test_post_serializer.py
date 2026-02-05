from django.test import TestCase
from ...serializers import PostSerializer
from ...models import Post
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class PostSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='some_password'
        )

    ### Field tests
    ## VALID
    def test_valid_title(self):
        """Validates that titles within length constraints (4-200) do not raise an error"""
        # testing the field directly avoids the "missing field" errors for the rest of the model
        field = PostSerializer().fields['title']
        # min_lenght = 4 < 'Hello' < max_lenght = 200
        valid_title = 'Hello'

        try:
            field.run_validators(valid_title)
        except ValidationError:
            # we don't really expect an error here, but its safer this way
            self.fail("unexpected ValidationError!")

    def test_valid_text_content(self):
        """Validates that text content within length constraints (15-4000) does not raise an error"""
        field = PostSerializer().fields['text_content']
        # min_lenght = 15; max_lenght = 4000
        valid_text_content = 'This is valid post content'

        try:
            field.run_validators(valid_text_content)
        except ValidationError:
            self.fail("unexpected ValidationError!")

    ##

    ## INVALID
    # title
    def test_title_length_too_short(self):
        """Tests if a ValidationError is raised when the title is below the 4 character minimum"""
        field = PostSerializer().fields['title']
        # min_length is 4
        too_short_title = 'Hi'

        with self.assertRaises(ValidationError):
            field.run_validators(too_short_title)

    def test_title_length_too_long(self):
        """Tests if a ValidationError is raised when the title is above the 200 character maximum"""
        field = PostSerializer().fields['title']
        # max_length is 200
        too_long_title = 'A' * 201

        with self.assertRaises(ValidationError):
            field.run_validators(too_long_title)
    #

    # text_content
    def test_text_content_length_too_short(self):
        """Tests if a ValidationError is raised when the text_content is below the 15 character minimum"""
        field = PostSerializer().fields['text_content']
        # min_length is 15
        too_short_text_content = 'too short'

        with self.assertRaises(ValidationError):
            field.run_validators(too_short_text_content)

    def test_text_content_length_too_long(self):
        """Tests if a ValidationError is raised when the title is above the 4000 character maximum"""
        field = PostSerializer().fields['text_content']
        # max_length is 200
        too_long_text_content = 'A' * 4001

        with self.assertRaises(ValidationError):
            # max_length is 200
            field.run_validators(too_long_text_content)
    #
    ##
    ###

    ### Profanity
    ## non-profane content is covered through the previous tests

    def test_title_profanity_integration_profane_content(self):
        """Verifies the title field correctly throws a ValidationError when profane language is used"""
        field = PostSerializer().fields['title']
        profane_title = 'Shit title'

        with self.assertRaises(ValidationError):
            field.run_validators(profane_title)

    def test_text_content_profanity_integration_profane_content(self):
        """Verifies the text_content field correctly throws a ValidationError when profane language is used"""
        field = PostSerializer().fields['text_content']
        profane_text_content = 'Fuck this profanity filter!'

        with self.assertRaises(ValidationError):
            field.run_validators(profane_text_content)


    ### Sanitization & Representation
    ## Sanitization (deserialization)
    def test_internal_value_sanitization(self):
        """Checks that HTML tags and whitespaces are stripped from input data during the deserialization (to_internal_value)"""
        unclean_data = {
            'title': '  <h1>Hello</h1>  ',
            'text_content': '<p>This is a long enough post to get through the checks.</p>',
            'image': 'https://example.com/image.png'
        }
        serializer = PostSerializer(data=unclean_data)

        # is.valid() calls the to_internal_value method of the serializer
        # adding ", serializer.errors" inside the assertTrue also prints the error message to the console
        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(serializer.validated_data['title'], 'Hello')
        self.assertEqual(serializer.validated_data['text_content'], 'This is a long enough post to get through the checks.')
    ##

    ## Representation (serialization)
    def test_representation_capitalizing_title(self):
        """Ensures the output data returns a Title Case version of the post title during serialization (to_representation)"""
        data = {
            'author': self.user,
            'title': 'this title should be capitalized',
            'text_content': 'This is a long enough post to get through the checks.',
            'image': 'https://example.com/image.png'
        }

        # .create() mocks writing raw values to the database ('INSERT INTO ...')
        post = Post.objects.create(**data)
        serializer = PostSerializer(post)

        self.assertEqual(serializer.data['title'], 'This Title Should Be Capitalized')
    ##
    ###