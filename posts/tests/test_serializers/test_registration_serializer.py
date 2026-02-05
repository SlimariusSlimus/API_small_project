from django.test import TestCase
from django.contrib.auth.models import User
from ...serializers import RegistrationSerializer, ProfanityValidator
from rest_framework.exceptions import ValidationError

class RegistrationSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "user",
            "password": "secure_password",
            "email": "example@example.com"
        }

    ### VALID
    def test_valid_user_data(self):
        """Ensures that correct data passes serializer validation"""
        serializer = RegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    ### INVALID
    def test_username_too_short(self):
        """Tests if a ValidationError is raised when the username is below the 4 character minimum"""
        too_short_username = 'Alf'
        field = RegistrationSerializer().fields['username']

        with self.assertRaises(ValidationError):
            field.run_validators(too_short_username)

    def test_username_too_long(self):
        """Tests if a ValidationError is raised when the username is above the 20 character maximum"""
        too_long_username = 'A' * 21
        field = RegistrationSerializer().fields['username']

        with self.assertRaises(ValidationError):
            field.run_validators(too_long_username)

    def test_password_too_short(self):
        """Tests if a ValidationError is raised when the password is below the 8 character minimum"""
        too_short_password = 'passwd'
        field = RegistrationSerializer().fields['password']

        with self.assertRaises(ValidationError):
            field.run_validators(too_short_password)

    def test_password_too_long(self):
        """Tests if a ValidationError is raised when the password is above the 50 character maximum"""
        too_long_password = 'A' * 51
        field = RegistrationSerializer().fields['password']

        with self.assertRaises(ValidationError):
            field.run_validators(too_long_password)

    def test_profane_username(self):
        """Verifies that the registration is blocked if the username contains profanity"""
        profane_user_data = {
            "username": "asshole",
            "password": "secure_password",
            "email": "example@example.com"
        }
        serializer = RegistrationSerializer(data=profane_user_data)
        # check if the serializer catches the username as invalid data
        self.assertFalse(serializer.is_valid())

        # username should be mentioned in the errors

        self.assertIn("username", serializer.errors)

    def test_create_user_hashes_password(self):
        """Confirms that the serializer stores passwords as secure hashes rather than plain text"""
        serializer = RegistrationSerializer(data=self.user_data)
        # raises an exception if the data is bad (so the .save() doesn't fail silently)
        serializer.is_valid(raise_exception=True)

        # trigger the .create() method. Returns the newly created User instance
        user = serializer.save()

        # django's built-in helper to verify the raw password matches the stored hash
        # it hashes the password again (with the same salt and algorithm) and compares both hashes
        self.assertTrue(user.check_password(self.user_data["password"]))

        # compares the database "password" field with the plain string "secure_password"
        self.assertNotEqual(user.password, self.user_data["password"])
