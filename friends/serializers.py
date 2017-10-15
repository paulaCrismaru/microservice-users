from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers


from friends.models import Friendship


class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class FriendshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friendship
        fields = ('sender', 'receiver', 'acceptance', 'id')

    def is_valid(self, raise_exception=False):
        if not super(FriendshipSerializer, self).is_valid(raise_exception=raise_exception):
            return False
        try:
            receiver = get_object_or_404(User, pk=self.validated_data['receiver'].pk)
            sender = get_object_or_404(User, pk=self.validated_data['sender'].pk)
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


class FriendshipDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friendship
        fields = ('sender', 'receiver', 'acceptance', 'id')

    def update(self, instance, validated_data):
        if "sender" in validated_data or "receiver" in validated_data:
            raise serializers.ValidationError({"detail": "You cannot change the sender or the receiver"})
        return super(FriendshipDetailSerializer, self).update(instance, validated_data)