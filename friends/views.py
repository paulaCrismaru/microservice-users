from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response

from friends.models import Friendship
from friends import serializers as friends_serializers


# /friendships/<pk>/
class FriendshipDetails(generics.RetrieveUpdateDestroyAPIView):

    queryset = Friendship.objects.all()
    serializer_class = friends_serializers.FriendshipDetailSerializer


# /friendships/
class RequestsList(generics.ListCreateAPIView):

    serializer_class = friends_serializers.CreateFriendshipSerializer
    queryset = Friendship.objects.all()

    def create(self, request, *args, **kwargs):
        data = {
            'sender': self.request.user.pk,
            'receiver': request.data['receiver']
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        friendship = Friendship(**serializer.validated_data)
        friendship.sender = self.request.user
        friendship.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
