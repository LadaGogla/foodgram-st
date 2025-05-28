from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Только владелец может изменять или удалять объект, остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user 