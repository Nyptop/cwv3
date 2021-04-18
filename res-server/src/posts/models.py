from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from django.conf import settings


def expiration():
    return now() + timedelta(seconds=30) #only 30 seconds so I can demonstrate that a post cannot be edited once expired.

TOPIC_CHOICES = (('Politics', 'Politics'),
              ('Tech', 'Tech'),
              ('Sports', 'Sports'),
              ('Health', 'Health'))

class Posts(models.Model):
    title = models.CharField(max_length=100)
    topic = MultiSelectField(choices=TOPIC_CHOICES)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    expiration_timestamp = models.DateTimeField(default=expiration)
    body = models.CharField(max_length=255)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="likes",blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="dislikes",blank=True)

    @property
    def is_expired(self):
        if now() > self.expiration_timestamp:
            return True
        return False
    
    @property
    def time_left(self):
        return self.expiration_timestamp - now()

    @property
    def interaction_count(self):
        #citation: [5]
        return self.likes.count() + self.dislikes.count()

class Comment(models.Model):
    #citation: [4]

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey('Posts', related_name='comments', on_delete=models.CASCADE)

    @property
    def time_left(self):
        return self.post.time_left

    @property
    def is_expired(self):
        return self.post.is_expired
