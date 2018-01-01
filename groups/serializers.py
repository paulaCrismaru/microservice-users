from collections import OrderedDict
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers


from groups.models import Membership


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username',)


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('name', 'id')


class GroupDetailsSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField(default=[])
    admins = serializers.SerializerMethodField(default=[])

    class Meta:
        model = Group
        fields = ('name', 'id', 'members', 'admins')

    @staticmethod
    def get_members(obj):
        return [membership.person.username for membership in Membership.objects.filter(group__pk=obj.pk)]

    @staticmethod
    def get_admins(obj):
        group_pk = obj.pk
        return [membership.person.username for membership in Membership.objects.filter(group__pk=group_pk)
                if membership.admin]


class CreateMembershipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = ('person', 'group', 'admin')


class MembershipSerializer(serializers.ModelSerializer):

    member_name = serializers.SerializerMethodField()
    membership_id = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ('person', 'member_name', 'admin', 'membership_id')

    @staticmethod
    def get_member_name(obj):
        if type(obj) is OrderedDict:
            return obj['person'].username
        return obj.person.username

    @staticmethod
    def get_membership_id(obj):
        return obj.pk


class MemberSerializer(serializers.ModelSerializer):

    member_name = serializers.SerializerMethodField()
    membership_id = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ('person', 'member_name', 'admin', 'membership_id')

    @staticmethod
    def get_member_name(obj):
        if type(obj) is OrderedDict:
            return obj['person'].username
        return obj.person.username

    @staticmethod
    def get_membership_id(obj):
        return obj.pk