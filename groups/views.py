from django.db import IntegrityError
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist

from rest_condition import Or

from rest_framework.response import Response
from rest_framework import generics, status

from groups.models import Membership
from groups.permissions.permissions import IsGroupMemberPermission, IsGroupAdminPermission
from groups.serializers import GroupDetailsSerializer, GroupSerializer, \
    MembershipSerializer, MemberSerializer, CreateMembershipSerializer


class GroupsList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        group = serializer.save()
        membership_serializer = CreateMembershipSerializer(data={'group': group.pk, 'person': user.pk, 'admin': True})
        if not membership_serializer.is_valid():
            return Response(membership_serializer.errors, status=400)
        membership_serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupDetails(generics.RetrieveUpdateDestroyAPIView):

    queryset = Group.objects.all()
    serializer_class = GroupDetailsSerializer
    permission_classes = (Or(IsGroupMemberPermission, IsGroupAdminPermission),)


class GroupMembers(generics.ListCreateAPIView):

    serializer_class = MembershipSerializer
    permission_classes = (Or(IsGroupMemberPermission, IsGroupAdminPermission),)

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return Membership.objects.filter(group__id=group_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_name = serializer.validated_data['person']
        try:
            serializer = self.perform_create(serializer)
        except IntegrityError:
            return Response({"detail": "User {} is already part of the group".format(user_name)},
                            status=status.HTTP_204_NO_CONTENT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        membership = Membership(**serializer.validated_data)
        group_id = self.kwargs['pk']
        membership.group = Group.objects.get(pk=group_id)
        membership.save()
        return MembershipSerializer(membership)


class GroupMembersDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = MemberSerializer
    lookup_url_kwarg = "membership_id"
    permission_classes = (Or(IsGroupAdminPermission, IsGroupMemberPermission),)

    def get_queryset(self):
        membership_id = self.kwargs['membership_id']
        group_id = self.kwargs['pk']
        try:
            return Membership.objects.filter(pk=membership_id, group__id=group_id)
        except ObjectDoesNotExist:
            return []
