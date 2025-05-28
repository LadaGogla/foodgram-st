from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только автор может изменять или удалять объект,
    остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user 

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только владелец может изменять или удалять объект,
    остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user 