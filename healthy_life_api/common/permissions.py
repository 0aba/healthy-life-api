from rest_framework import permissions


class IsModeratorOrSuperUser(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        return request.user.is_authenticated and request.user.groups.filter(name='Модератор').exists()


class IsPharmacistOrSuperUser(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True

        return request.user.is_authenticated and request.user.groups.filter(name='Фармацевт').exists()


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)

        return request.method in permissions.SAFE_METHODS or is_admin
