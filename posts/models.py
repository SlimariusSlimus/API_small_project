from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    text_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True, null=True)  # for simplicity's sake only using URL here

    def __str__(self):
        return f"Post '{self.title}' by '{self.author}' posted at {self.timestamp}"

class Comment(models.Model):
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment '{self.text_content}' by '{self.author}' posted at {self.timestamp}"
