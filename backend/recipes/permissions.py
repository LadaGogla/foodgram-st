from rest_framework import permissions


class BaseOwnerPermission(permissions.BasePermission):
    """
    Базовый класс для проверки прав доступа к объекту.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.check_ownership(request, obj)

    def check_ownership(self, request, obj):
        raise NotImplementedError(
            'Метод check_ownership должен быть реализован в дочернем классе'
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только автор/владелец может изменять или удалять объект,
    остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return getattr(obj, 'author', None) == request.user or getattr(obj, 'user', None) == request.user


class IsOwnerOrReadOnly(BaseOwnerPermission):
    """
    Разрешение: только владелец может изменять или удалять объект,
    остальные могут только читать.
    """
    def check_ownership(self, request, obj):
        return obj.user == request.user 


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: Администратор имеет полные права, автор может изменять и удалять, остальные только читать.
    """
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True

        
        if request.method == 'POST' and request.user.is_authenticated:
            return True
            
        
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True

        
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        
        return getattr(obj, 'author', None) == request.user 