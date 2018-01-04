from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions

from groups.models import Membership

not_safe_methods = ["POST", "PATCH", "PUT", "DELETE"]


class IsGroupMemberPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in not_safe_methods:
            return False
        user_id = get_user_model().objects.get(username=request.user).pk
        group_id = view.kwargs['pk']
        try:
            Membership.objects.get(person__id=user_id, group__id=group_id)
            return True
        except ObjectDoesNotExist:
            return False


class IsGroupAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_model().objects.get(username=request.user).pk
        group_id = view.kwargs['pk']
        try:
            membership = Membership.objects.get(person__id=user_id, group__id=group_id)
            return membership.admin
        except ObjectDoesNotExist:
            return False