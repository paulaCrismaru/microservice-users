from rest_framework import serializers

from django.contrib.auth.models import User
from models import Friendships


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class FriendshipSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')
    receiver = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Friendships
        fields = ('sender', 'receiver', 'acceptance')


class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)
