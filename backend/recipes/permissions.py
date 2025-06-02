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
        # Проверяем либо creator, либо user в зависимости от модели
        return getattr(obj, 'creator', None) == request.user or obj.user == request.user


class IsOwnerOrReadOnly(BaseOwnerPermission):
    """
    Разрешение: только владелец может изменять или удалять объект,
    остальные могут только читать.
    """
    def check_ownership(self, request, obj):
        return obj.user == request.user 