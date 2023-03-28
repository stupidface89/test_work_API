import json

from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class TestModels(APITestCase):
    """
    Тестирование моделей приложения Users
    """
    def setUp(self) -> None:
        self.unauthorized_user = APIClient()
        self.user_data = json.dumps({'email': 'alex88@mail.ru',
                                     'password': 'e12345678'})

        self.url = reverse('create_user')

    def tearDown(self) -> None:
        pass

    def test_user_create(self):
        """
        Тестирование создания пользователя
        """
        self.unauthorized_user.post(self.url,
                                    data=self.user_data,
                                    content_type='application/json')
        get_user = User.objects.filter(
            email__iexact=json.loads(self.user_data).get('email')).first()

        # Проверяем что пользователь был создан
        self.assertEqual(get_user.email, json.loads(self.user_data).get('email'))

        # Проверяем что пользователь после создания не имеет прав стафа или суперюзера
        self.assertEqual((get_user.is_staff or get_user.is_superuser), False)

        # Проверяем что у нового пользователя аттрибут is_active имеет значение True
        self.assertEqual(get_user.is_active, True)

    def test_create_with_not_valid_email(self):
        """
        Пользователь с невалидным email не создается
        """
        not_valid_email = 'asd.ru'
        data = json.dumps({'email': not_valid_email, 'password': 'e12345678'})
        self.unauthorized_user.post(self.url, data=data, content_type='application/json')

        response = self.unauthorized_user.post(self.url,
                                               data=json.dumps({'password': 'e12345678'}),
                                               content_type='application/json')

        # После запроса сервер возвращает код ответа 400
        self.assertEqual(response.status_code, 400)

        # Пользователя в БД нет
        self.assertEqual(User.objects.filter(email__iexact=not_valid_email).first(), None)

    def test_create_with_not_valid_password(self):
        """
        Пользователь с невалидным паролем не создается
        """
        not_valid_password = '12345'
        data = json.dumps({'email': 'pops100@gmail.com', 'password': not_valid_password})
        response = self.unauthorized_user.post(self.url, data=data, content_type='application/json')

        # Код ответа 400
        self.assertEqual(response.status_code, 400)

        # Пользователя в БД нет
        self.assertEqual(User.objects.filter(email__iexact='pops100@gmail.com').first(), None)

    def test_email_is_not_capitalized(self):
        """
        После создания пользователь в БД записывается email в нижнем регистре.
        """
        email = 'MoScOW@maIL.rU'
        data = json.dumps({'email': email, 'password': 'e1712023210'})

        self.unauthorized_user.post(self.url, data=data, content_type='application/json')

        get_user = User.objects.filter(email__iexact=email).first()

        self.assertEqual(get_user.email, email.lower())

    def test_create_with_already_taken_email(self):
        """
        Пользователь с email уже существует в базе
        """
        user_data = {'email': 'misha2007@gmail.com', 'password': 'e12345678'}
        User.objects.create(**user_data)

        response = self.unauthorized_user.post(self.url,
                                               json.dumps(user_data),
                                               content_type='application/json')

        get_users = User.objects.filter(email__iexact=user_data.get('email'))

        # Проверяем что код ответа 400
        self.assertEqual(response.status_code, 400)

        # Количество пользователей в БД с заданным email - 1 шт.
        self.assertEqual(get_users.count(), 1)
