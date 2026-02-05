import json
import os
from rest_framework import serializers
from django.utils.html import strip_tags
from .models import Comment, Post
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

def load_profane_words():
    """Imports a list of banned words from a json file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'resources', 'profanity_words_list.json')

    try:
        with open(file_path, 'r') as f:
            banned_words = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # fallback to an empty list if file is missing or broken
        banned_words = []

    return banned_words

PROFANE_WORDS = load_profane_words()


class ProfanityValidator:
    """
    Makes sure that there are no curse or swearwords etc in the titles or text bodies.
    For the sake of simplicity, there are no checks to prevent false positives (eg. C'ass'andra and so on)
    and we only cover the english language.
    """
    def __init__(self):
        self.profane_words = PROFANE_WORDS

    def __call__(self, value):
        for word in self.profane_words:
            if word.lower() in value.lower():
                raise ValidationError(f'The word "{word}" is not allowed (profanity filter).')

class CommentSerializer(serializers.ModelSerializer):
    # this displays the author as a human-readable name rather than an ID
    # no profanity filter for the author as we would take care of this in the custom user model on account creation
    # no validation for the timestamp as it is handled internally
    author = serializers.ReadOnlyField(source='author.username')
    text_content = serializers.CharField(min_length=15, max_length=4000, validators=[ProfanityValidator(), ])

    class Meta:
        model = Comment
        fields = ['id', 'parent_post', 'author', 'text_content', 'timestamp']

    def to_internal_value(self, data):
        """Sanitization"""
        if 'text_content' in data:
            data['text_content'] = strip_tags(data['text_content']).strip()
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    title = serializers.CharField(min_length=4, max_length=200, validators=[ProfanityValidator(), ])
    text_content = serializers.CharField(min_length=15, max_length=4000, validators=[ProfanityValidator(), ])
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'text_content', 'timestamp', 'image', 'comments']

    def to_internal_value(self, data):
        """Sanitization"""
        if 'title' in data:
            data['title'] = strip_tags(data['title']).strip()
        if 'text_content' in data:
            data['text_content'] = strip_tags(data['text_content']).strip()
        # after our manual intervention, continue regulary
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Formatting the post Title"""
        # get the standard dictionary from the parent class
        representation = super().to_representation(instance)

        if instance.title:
            # alternatively we could use capitalize() here, depending on preference
            representation['title'] = instance.title.title()

        return representation


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration by validating username and password,
    ensuring the username is not profane
    """
    # we don't need to specify uniqueness for the username here, because it is handled through the User model
    username = serializers.CharField(min_length=4, max_length=20, validators=[ProfanityValidator(), ])
    password = serializers.CharField(min_length=8, max_length=50)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        """
        Overrides the default create method to use django's create_user helper,
        which ensures that the password is hashed before saving to the database
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
