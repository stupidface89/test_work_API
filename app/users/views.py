from rest_framework import generics, status
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema

from users.models import UserManager
from users.serializers import CreateUserSerializer


@extend_schema_view(
    create=extend_schema(description='Создание нового пользователя', tags=['Users']),
)
class UserCreate(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            manager = UserManager()
            if manager.check_if_exists(serializer.data.get('email')):
                msg = 'Пользователь с таким email уже существует'
                raise ValidationError(msg, code='unique')

            manager.create_user(**serializer.data)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
