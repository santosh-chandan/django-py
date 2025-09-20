from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """Allow only owners to edit objects, everyone else can only read"""
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to anyone
        if request.method in SAFE_METHODS:
            return True
        # Write permissions only for owner
        return obj.user == request.user
