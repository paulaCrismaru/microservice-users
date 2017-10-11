from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User, Group
from rest_framework import serializers

from models import Friendships

import utils


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email','user_id')

    @staticmethod
    def get_user_id(obj):
        return utils.encode(obj.id)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        if validated_data.get('email'):
            try:
                User.objects.get(email=validated_data['email'])
            except ObjectDoesNotExist:
                pass
            else:
                raise ValidationError("A user with that email already exists.")
        return User.objects.create_user(**validated_data)


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


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='string_date', default=utils.get_now_string)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('name', 'id', 'is_member')

    def get_is_member(self, obj):
        if self.context.get('request'):
            return self.context.get('request').user in obj.user_set.all()
        return False


class GroupDetailsSerializer(GroupSerializer):
    members = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField(default=[])

    class Meta:
        model = Group
        fields = ('name', 'id', 'members', 'is_member', 'admins')

    @staticmethod
    def get_members(obj):
        return [u.username for u in obj.user_set.all()]

    @staticmethod
    def get_admins(obj):
        return [a.username for a in obj.admins.all()]


class CreateGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('name', 'id', 'is_member')