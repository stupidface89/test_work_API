from rest_framework.serializers import ModelSerializer, EmailField, CharField
from rest_framework.serializers import ValidationError
from django.contrib.auth import password_validation, get_user_model
from django.core import exceptions


User = get_user_model()


class CreateUserSerializer(ModelSerializer):
    email = EmailField(required=True)
    password = CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate(self, data):
        user = User(**data)
        password = data.get('password')

        errors = dict()
        try:
            password_validation.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise ValidationError(errors)
        return super(CreateUserSerializer, self).validate(data)
