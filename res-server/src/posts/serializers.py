from rest_framework import serializers
from .models import Posts
from .models import Comment
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    #citation: [4]

    class Meta:
        model = Comment
        fields = ('id','creation_timestamp', 'body', 'user_id', 'post','time_left','is_expired')
    
    def validate(self, data):
        post = data['post']
        if post.is_expired == True:
            raise serializers.ValidationError("Post has expired")
        return data

class PostsSerializer(serializers.ModelSerializer):
    #citation [6]
    comments = CommentSerializer(many=True,source='comments.all',required=False) 

    class Meta:
        model = Posts
        fields = ('id','is_expired','title','topic','creation_timestamp','expiration_timestamp','body','user_id','likes','dislikes','is_expired','time_left','interaction_count','comments') 


