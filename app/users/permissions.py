from rest_framework import permissions

from diary.models import Diary, Note


class IsOwnerOrReadOnlyPermission(permissions.BasePermission):
    """
    Пермишен-Класс определяет, есть ли у пользователя права на редактирование
    или удаление страниц/дневника
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_staff or request.user.is_superuser:
            return True

        if isinstance(obj, Diary):
            return obj.owner == request.user

        if isinstance(obj, Note):
            return obj.diary.owner == request.user

    def has_permission(self, request, view) -> bool:
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_authenticated)
