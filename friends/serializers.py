import collections

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers


from friends.models import Friendship


class CreateFriendshipSerializer(serializers.ModelSerializer):

    receiver_username = serializers.SerializerMethodField()

    @staticmethod
    def get_receiver_username(obj):
        if type(obj) is collections.OrderedDict:
            return obj['receiver'].username
        return obj.receiver.username

    class Meta:
        model = Friendship
        fields = ('id', 'receiver', 'receiver_username')

    def is_valid(self, raise_exception=False):
        if not super(CreateFriendshipSerializer, self).is_valid(raise_exception=raise_exception):
            return False
        if self.initial_data['receiver'][0] == self.initial_data['sender']:
            return False
        try:
            receiver = get_object_or_404(User, pk=self.initial_data['receiver'][0])
            sender = get_object_or_404(User, pk=self.initial_data['sender'])
        except ValueError:
            if raise_exception:
                raise NotFound()
            return False
        try:
             Friendship.objects.get(sender=sender, receiver=receiver)
        except ObjectDoesNotExist:
            pass
        else:
            if raise_exception:
                raise ValidationError({"detail": "A request to this user already exists"})
            return False
        try:
            Friendship.objects.get(receiver=sender, sender=receiver)
        except ObjectDoesNotExist:
            pass
        else:
            if raise_exception:
                raise ValidationError({"detail": "A request from this user already exists"})
            return False
        return True


class RequestDetailSerializer(serializers.ModelSerializer):

    sender_username = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('sender', 'sender_username', 'acceptance', 'id')

    def update(self, instance, validated_data):
        if "sender" in validated_data or "receiver" in validated_data:
            raise serializers.ValidationError({"detail": "You cannot change the sender or the receiver"})
        return super(RequestDetailSerializer, self).update(instance, validated_data)

    @staticmethod
    def get_sender_username(obj):
        return obj.sender.username

    @staticmethod
    def get_sender(obj):
        return obj.sender.pk


class FriendSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('id', 'username')

    @staticmethod
    def get_sender_username(obj):
        return obj.sender.username

    @staticmethod
    def get_receiver_username(obj):
        return obj.receiver.username

    def get_username(self, obj):
        current_user = (self.context['request'].user)
        if obj.sender == current_user:
            return obj.receiver.username
        return obj.sender.username
