from django.test import TestCase
from django.contrib.auth.models import User
from ...serializers import ProfanityValidator
from ...models import Post, Comment
from rest_framework.exceptions import ValidationError


class ProfanityValidatorTests(TestCase):
    def setUp(self):
        self.validator = ProfanityValidator()

    def test_valid_text(self):
        """A clean text should not raise an error"""
        # if the line below raises an exception (which it shouldn't), the test automatically fails
        self.validator("This is a harmless text.")

    def test_profane_text(self):
        """Ensures that banned words are not passing the validator"""
        text = "Fuck! This is NOT a harmless text!"
        # the 'with' catches the expected error. Otherwise the exception would be thrown prematurely
        with self.assertRaises(ValidationError):
            self.validator(text)
