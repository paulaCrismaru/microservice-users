from django.contrib.auth.models import Group
from rest_framework import serializers

from api import utils


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