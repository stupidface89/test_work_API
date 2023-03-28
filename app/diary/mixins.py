class CheckObjectPermissionsMixin:
    """
    Проверка прав пользователя на возможность удаления или обновления объекта
    """
    def perform_update(self, serializer):
        self.check_object_permissions(self.request, self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, self.get_object())
        instance.delete()


class SendKwargsInContextMixin:
    """
    Добавляет в контекст доп. аттрибуты, перед передачей в сериализатор
    """
    def get_serializer_context(self):
        context = super(SendKwargsInContextMixin, self).get_serializer_context()

        context.update({**self.kwargs})
        return context


class InstanceRequestInContextMixin:
    """
    Добавляет в контекст объект request, перед передачей в сериализатор
    """
    def get_serializer_context(self):
        context = super(InstanceRequestInContextMixin, self).get_serializer_context()

        context.update({"request": self.request})
        return context
