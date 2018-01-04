from rest_framework.permissions import IsAuthenticated

not_safe_methods = ["POST", "PATCH", "PUT", "DELETE"]


class NotIsAuthenticated(IsAuthenticated):

    def has_permission(self, request, view):
        if request.method not in not_safe_methods:
            return True
        return not super(NotIsAuthenticated, self).has_permission(request, view)