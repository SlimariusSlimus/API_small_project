from django.contrib.auth.models import User
from ...models import Post, Comment
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


# using APITestCase here because it provides self.client which is specialized for JSON requests
class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='some_password'
        )
        self.url = reverse('auth-login')

    ### VALID
    def test_successful_login_new_token(self):
        """Confirms that login works and returns a freshly created token"""
        data = {
            "username": self.user.username,
            "password": "some_password"  # can't use self.user.password as it would already be hashed
        }
        # does the POST request. format='json' tells DRF to set headers correctly (json instead of form)
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get the token object from the DB for this user
        db_token = Token.objects.get(user=self.user)

        # compare both keys response.data['token'] (the token from the response) and db_token.key (from the database)
        self.assertEqual(response.data['token'], db_token.key)

    def test_successful_login_with_existing_token(self):
        """Confirms that login returns a freshly created token even if a token already exists"""
        # we're creating an old token manually
        old_token = Token.objects.create(user=self.user).key
        data = {
            "username": self.user.username,
            "password": "some_password"  # can't use self.user.password as it would already be hashed
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify that the new token doesn't match the old token
        self.assertNotEqual(response.data['token'], old_token)

        # ensure the old token is actually gone from the database
        self.assertFalse(Token.objects.filter(key=old_token).exists())

        # get the token object from the DB for this user
        db_token = Token.objects.get(user=self.user).key

        # compare both keys response.data['token'] (the token from the response) and the freshly created db_token.key (from the database)
        self.assertEqual(response.data['token'], db_token)

    ### INVALID
    def test_authentication_existing_user_wrong_username(self):
        data = {
            "username": "usernäme",  # wrong/non-existing username
            "password": "some_password"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_existing_user_wrong_password(self):
        data = {
            "username": "username",
            "password": "some_passwörd"  # wrong password
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_empty_data(self):
        data = {}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.valid_data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "secure_password123"
        }

    ### VALID
    def test_registration_valid_data(self):
        """Confirms that registration with valid data works and returns a token"""
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if user with our username exists in the database
        self.assertTrue(User.objects.filter(username="new_user").exists())

        # verify that a token was created for the new user
        user = User.objects.get(username="new_user")
        db_token = Token.objects.get(user=user).key

        self.assertEqual(response.data['token'], db_token)
        self.assertEqual(response.data['user']['username'], "new_user")

    def test_registration_missing_email(self):
        """Confirms that the registration succeeds with missing email as it is not a required field"""
        incomplete_data_missing_name = {
            "username": "new_user",
            "password": "secure_password123"
        }
        response = self.client.post(self.url, incomplete_data_missing_name, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    ### INVALID
    def test_registration_missing_username(self):
        """Confirms taht the registration fails with missing username"""
        incomplete_data_missing_name = {
            "email": "new_user@example.com",
            "password": "secure_password123"
        }
        response = self.client.post(self.url, incomplete_data_missing_name, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_password(self):
        """Confirms taht the registration fails with missing password"""
        incomplete_data_missing_name = {
            "username": "new_user",
            "email": "new_user@example.com",
        }
        response = self.client.post(self.url, incomplete_data_missing_name, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_empty_data(self):
        """Confirms taht the registration fails with empty data"""
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
