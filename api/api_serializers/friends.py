from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from rest_framework import serializers


from api.models import Friendships


class FriendshipSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    receiver = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Friendships
        fields = ('sender', 'receiver', 'acceptance', 'uuid')


class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class SenderSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Friendships
        fields = ('uuid', 'acceptance', 'receiver')

    @staticmethod
    def get_receiver(obj):
        return obj.receiver.username


class ReceiverSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Friendships
        fields = ('uuid', 'acceptance', 'sender')

    @staticmethod
    def get_receiver(obj):
        return obj.sender.username
