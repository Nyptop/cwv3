from django.shortcuts import render
from rest_framework import viewsets
from .models import Posts
from .serializers import PostsSerializer
from rest_framework import filters
from django_filters import rest_framework as filters
import django_filters
from django_property_filter import PropertyFilterSet, PropertyNumberFilter
from django_property_filter import PropertyBooleanFilter, PropertyOrderingFilter
from .models import Comment
from rest_framework import generics
from .serializers import CommentSerializer
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import datetime
from django.db.models import Max
from django.utils.timezone import now
from django.db.models import Count


class PostFilterSet(PropertyFilterSet):
    is_expired = PropertyBooleanFilter(field_name = "is_expired")
    topic = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Posts
        fields = ['is_expired','topic']

class PostsViewSet(viewsets.ModelViewSet):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    filterset_class = PostFilterSet

class CommentList(generics.ListCreateAPIView):
    #citation: [4]

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    #citation: [4]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


@api_view(['GET'])
def interaction_count_view(request,is_expired,topic):
    #citation: [2]

    #this section is filtering based on whether the post is expired and the topic specified
    posts = Posts.objects.all()
    if is_expired == "True":
        posts = posts.filter(expiration_timestamp__lte=now())
    elif is_expired == "False":
        posts = posts.filter(expiration_timestamp__gte=now())
    posts = posts.filter(topic__icontains=topic)
    if not posts:
        return Response({"No items match the query"})

    #this part returns the response with the most interactions now that Posts has been filtered
    max_post = posts.annotate(interactions=Count('likes') + Count('dislikes')).latest('interactions')
    if max_post:
        return Response({"Post number" :  max_post.pk, "interaction_count": max_post.interactions})
    return Response({"Post number": None, "interaction_count": 0, "message": "No posts exist!"})



@api_view(['POST'])
def like_view(request, pk, destination): #destination is the user's id

    post = Posts.objects.get(pk=pk)

    if post.is_expired == True:
        print("expired")
        return Response({"message":"post expired"})

    if check_self_action(destination,post):
        return Response({"message":"cannot like own post"})

    liked = check_like(destination, post)

    prefix = ""

    if liked:
        post.likes.remove(destination)
        prefix = "un"
    else:
        post.likes.add(destination) 

    return Response({"Message":f"Post {pk} successfully {prefix}liked by {destination}"})

@api_view(['POST'])
def dislike_view(request, pk, destination): #destination is the user's id

    post = Posts.objects.get(pk=pk)

    if post.is_expired == True:
        return Response({"message","post expired"})

    if check_self_action(destination,post):
        return Response({"message","cannot dislike own post"})

    disliked = check_dislike(destination, post)

    prefix = ""

    if disliked:
        post.dislikes.remove(destination)
        prefix = "un"
    else:
        post.dislikes.add(destination) 

    return Response({"Message":f"Post {pk} successfully {prefix}disliked by {destination}"})

def check_self_action(destination,post):
    post_owner = post.user_id
    return destination == post_owner.id

def check_like(destination, post):
    #citation: [3]

    likes = post.likes
    if destination in [user.id for user in likes.all()]:
        return True
    return False

def check_dislike(destination, post):
    #citation: [3]

    dislikes = post.dislikes
    if destination in [user.id for user in dislikes.all()]:
        return True
    return False