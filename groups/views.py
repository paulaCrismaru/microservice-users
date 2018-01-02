from django.db import IntegrityError
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import generics, status

from groups.models import Membership
from groups.serializers import GroupDetailsSerializer, GroupSerializer, \
    MembershipSerializer, MemberSerializer


def is_group_admin(group_id, user_id):
    try:
        membership = Membership.objects.get(person__id=user_id, group__id=group_id)
        return membership.admin
    except ObjectDoesNotExist:
        return True


class GroupsList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        group = serializer.save()
        membership_serializer = MembershipSerializer(data={'group': group.pk, 'person': user.pk, 'admin': True})
        if not membership_serializer.is_valid():
            return Response(membership_serializer.errors, status=400)
        membership_serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupDetails(generics.RetrieveUpdateDestroyAPIView):

    queryset = Group.objects.all()
    serializer_class = GroupDetailsSerializer

    def update(self, request, *args, **kwargs):
        group_id = self.kwargs['pk']
        user_id = User.objects.get(username=request.user).pk
        if is_group_admin(group_id, user_id):
            return super(GroupDetails, self).update(request, *args, **kwargs)
        else:
            return Response({"detail": "Only admins cand rename the group"}, status=status.HTTP_400_BAD_REQUEST)


class GroupMembers(generics.ListCreateAPIView):

    serializer_class = MembershipSerializer

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

    def get_queryset(self):
        membership_id = self.kwargs['membership_id']
        group_id = self.kwargs['pk']
        try:
            return Membership.objects.filter(pk=membership_id, group__id=group_id)
        except ObjectDoesNotExist:
            return []

    def update(self, request, *args, **kwargs):
        group_id = self.kwargs['pk']
        user_id = User.objects.get(username=request.user).pk
        if is_group_admin(group_id, user_id):
            return super(GroupMembersDetail, self).update(request, *args, **kwargs)
        return Response({"detail": "Only admins can update information"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        group_id = self.kwargs['pk']
        user_id = User.objects.get(username=request.user).pk
        if is_group_admin(group_id, user_id):
            return super(GroupMembersDetail, self).destroy(request, *args, **kwargs)
        return Response({"detail": "Only admins can remove users"}, status=status.HTTP_400_BAD_REQUEST)
