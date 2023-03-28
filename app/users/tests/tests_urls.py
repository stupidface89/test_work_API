import json

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import generics, viewsets

User = get_user_model()


class TestUrls(APITestCase):
    """
    Тестирование урлов приложения Users на доступность и соответствие кодов ответа.
    Бизнес логика не тестируется.
    """

    def setUp(self) -> None:
        # Выключаем защиту от троттлинга
        viewsets.GenericViewSet.throttle_classes = ()
        generics.GenericAPIView.throttle_classes = ()

        self.unauthorized_user = APIClient()

    def tearDown(self) -> None:
        pass

    def test_create_user_url(self):
        """
        Тестирование урла создания нового пользователя api/v1/users/create-user
        """
        create_user_url = reverse('create_user')

        # GET Запрос
        self.assertEqual(self.unauthorized_user.get(create_user_url).status_code, 405)

        # POST с пустым телом
        self.assertEqual(self.unauthorized_user.post(create_user_url).status_code, 400)

        # POST с данными
        self.assertEqual(
            self.unauthorized_user.post(create_user_url,
                                        data=json.dumps({'email': 'franko99@gmail.com',
                                                         'password': 'e12345678'}),
                                        content_type='application/json').status_code, 201)
