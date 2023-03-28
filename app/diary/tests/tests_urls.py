import uuid
import json

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets
from rest_framework.test import APITestCase, APIClient

from diary.models import Diary, Note

User = get_user_model()


class TestsUrls(APITestCase):
    """
    Тестирование урлов приложения Diary, на доступность и соответствие кодов ответа.
    Бизнес логика не тестируется.
    """
    def setUp(self) -> None:
        viewsets.GenericViewSet.throttle_classes = ()
        generics.GenericAPIView.throttle_classes = ()

        self.unauthorized_client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client_1 = APIClient()

        # Создаём пользователя и делаем последующий запрос токена, для осуществления
        # авторизованных запросов
        self.user_data = {'email': 'Basyan2002@mail.ru', 'password': 'e12345678'}
        self.user_data_1 = {'email': 'Vasyan2003@mail.ru', 'password': 'asd123mon'}
        self.user_data_2 = {'email': 'Gasyan2000@mail.ru', 'password': 'asd123mon'}

        self.user = User.objects.create_user(**self.user_data)
        self.user_1 = User.objects.create_user(**self.user_data_1)
        self.user_2 = User.objects.create_user(**self.user_data_2)

        response = self.authorized_client.post(reverse('token_obtain_pair'),
                                               self.user_data, format='json')
        token = response.data['access']
        self.authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.authorized_client_1.post(reverse('token_obtain_pair'),
                                                 self.user_data_2, format='json')
        token = response.data['access']
        self.authorized_client_1.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.test_diary_public = Diary.objects.create(title='Публичный дневник для тестирования',
                                                      owner_id=self.user.id,
                                                      kind='public')

        self.test_diary_private = Diary.objects.create(title='Приватный дневник для тестирования',
                                                       owner_id=self.user.id,
                                                       kind='public')

        self.test_diary_public = Diary.objects.create(title='Публичный дневник',
                                                      owner_id=self.user.id,
                                                      kind='public')

        self.test_diary_public_1 = Diary.objects.create(title='Публичный дневник_1',
                                                        owner_id=self.user_1.id,
                                                        kind='public')

        self.test_diary_private = Diary.objects.create(title='Приватный дневник_1',
                                                       owner_id=self.user_1.id,
                                                       kind='private')

        self.test_note_public_diary = Note.objects.create(text='Запись в публичном дневнике',
                                                          diary_id=self.test_diary_public.id)

        self.test_note_private_diary = Note.objects.create(text='Запись в приватном дневнике',
                                                           diary_id=self.test_diary_private.id)

    def tearDown(self) -> None:
        pass

    def test_diary_list_create(self):
        """
        Тест urla api/v1/diary/ :методы GET, POST
        """

        # Метод GET
        # Авторизованный пользователь получает все дневники
        self.assertEqual(self.authorized_client.get(
            reverse('diaries_list_create')
        ).status_code, 200)

        # Неавторизованный пользователь получает все дневники
        self.assertEqual(self.unauthorized_client.get(
            reverse('diaries_list_create')
        ).status_code, 401)

        # Метод POST
        # Авторизованный пользователь создает дневник
        self.assertEqual(self.authorized_client.post(
            reverse('diaries_list_create'),
            data=json.dumps({"title": "my dear diary", "kind": "public"}),
            content_type="application/json"
        ).status_code, 201)

        # Неавторизованный пользователь создает дневник
        self.assertEqual(self.unauthorized_client.post(
            reverse('diaries_list_create'),
            data=json.dumps({"title": "my dear diary", "kind": "public"}),
            content_type="application/json"
        ).status_code, 401)

        # Авторизованный пользователь создает дневники с некорректными данными
        self.assertEqual(self.authorized_client.post(
            reverse('diaries_list_create'), data=json.dumps({"": ""}),
            content_type="application/json"
        ).status_code, 400)

    def test_user_profile(self):
        """
        Тест urla api/v1/diary/profile/ :методы GET
        """
        # Метод GET
        # Авторизованный пользователь получает собственные дневники
        self.assertEqual(self.authorized_client.get(
            reverse('user_profile')
        ).status_code, 200)

        # Неавторизованный пользователь пытается получить собственные дневники
        self.assertEqual(self.unauthorized_client.get(
            reverse('user_profile')
        ).status_code, 401)

    def test_user_list_diaries(self):
        """
        Тест urla api/v1/diary/profile/<uuid:user_id> :методы GET
        """
        # Метод GET
        # Авторизованный пользователь получает дневники пользователя
        self.assertEqual(self.authorized_client.get(
            reverse('user_list_diaries', kwargs={"user_id": self.user_1.id})
        ).status_code, 200)

        # Неавторизованный пользователь получает дневники пользователя
        self.assertEqual(self.unauthorized_client.get(
            reverse('user_list_diaries', kwargs={"user_id": self.user_1.id})
        ).status_code, 401)

        # Авторизованный пользователь получает дневники несуществующего пользователя
        self.assertEqual(self.authorized_client.get(
            reverse('user_list_diaries', kwargs={'user_id': uuid.uuid4()})).status_code, 404)

    def test_get_diary_detail(self):
        """
        Тест urla api/v1/diary/<uuid:diary_id>/ :методы GET, PATCH, DELETE
        """

        # Метод GET
        # Авторизованный пользователь читает публичный дневник
        self.assertEqual(self.authorized_client.get(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public_1.id})
        ).status_code, 200)

        # Неавторизованный пользователь читает публичный дневник
        self.assertEqual(self.unauthorized_client.get(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public_1.id})
        ).status_code, 401)

        # Авторизованный пользователь читает несуществующий дневник
        self.assertEqual(self.authorized_client.get(
            reverse('get_diary_detail', kwargs={'diary_id': uuid.uuid4()})
        ).status_code, 404)

        # Метод PATCH
        # Авторизованный пользователь изменяет свой дневник
        data = {"title": "New diary title"}
        self.assertEqual(self.authorized_client.patch(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public.id}),
            data=json.dumps(data), content_type='application/json'
        ).status_code, 200)

        # Неавторизованный пользователь изменяет дневник
        self.assertEqual(self.unauthorized_client.patch(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public.id}),
            data=json.dumps(data), content_type='application/json'
        ).status_code, 401)

        # Авторизованный пользователь изменяет несуществующий дневник
        self.assertEqual(self.authorized_client.patch(
            reverse('get_diary_detail', kwargs={'diary_id': uuid.uuid4()}),
            data=json.dumps(data), content_type='application/json'
        ).status_code, 404)

        # Метод DELETE
        # Авторизованный пользователь удаляет свой дневник
        self.assertEqual(self.authorized_client.delete(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public.id})
        ).status_code, 204)

        # Неавторизованный пользователь удаляет дневник
        self.assertEqual(self.unauthorized_client.delete(
            reverse('get_diary_detail', kwargs={'diary_id': self.test_diary_public_1.id})
        ).status_code, 401)

        # Авторизованный пользователь удаляет несуществующий дневник
        self.assertEqual(self.authorized_client.delete(
            reverse('get_diary_detail', kwargs={'diary_id': uuid.uuid4()})
        ).status_code, 404)

    def test_notes_list(self):
        # Метод GET
        # Авторизованный пользователь запрашивает записи с публичного дневника
        self.assertEqual(self.authorized_client.get(
            reverse('notes_list', kwargs={'diary_id': self.test_diary_public.id})
        ).status_code, 200)

        # Неавторизованный пользователь запрашивает записи с публичного дневника
        self.assertEqual(self.unauthorized_client.get(
            reverse('notes_list', kwargs={'diary_id': self.test_diary_public.id})
        ).status_code, 401)

        # Авторизованный пользователь запрашивает записи у несуществующего дневника
        self.assertEqual(self.authorized_client.get(
            reverse('notes_list', kwargs={'diary_id': uuid.uuid4()})
        ).status_code, 404)

        # Метод POST
        # Авторизованный пользователь создает запись в своем дневнике
        self.assertEqual(self.authorized_client.post(
            reverse('notes_list', kwargs={'diary_id': self.test_diary_public.id}),
            data=json.dumps({'text': 'somebody wants icecream'}),
            content_type='application/json'

        ).status_code, 201)

        # Неавторизованный пользователь создает запись в дневнике
        self.assertEqual(self.unauthorized_client.post(
            reverse('notes_list', kwargs={'diary_id': self.test_diary_public.id}),
            data=json.dumps({'text': 'somebody wants icecream'}),
            content_type='application/json'
        ).status_code, 401)

        # Авторизованный пользователь создает запись в своем дневнике с некорректными данными
        self.assertEqual(self.authorized_client.post(
            reverse('notes_list', kwargs={'diary_id': self.test_diary_public.id}),
            data=json.dumps({"": ""}),
            content_type='application/json'
        ).status_code, 400)

        # Авторизованный пользователь создает запись в несуществующем дневнике
        self.assertEqual(self.authorized_client.post(
            reverse('notes_list', kwargs={'diary_id': uuid.uuid4()}),
            data=json.dumps({'text': 'somebody wants icecream'}),
            content_type='application/json'
        ).status_code, 404)

    def test_get_note_detail(self):
        # Метод GET
        # Авторизованный пользователь читает запись из дневника
        self.assertEqual(self.authorized_client.get(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id})
        ).status_code, 200)

        # Неавторизованный пользователь читает запись из дневника
        self.assertEqual(self.unauthorized_client.get(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id})
        ).status_code, 401)

        # Авторизованный пользователь читает несуществующую запись из дневника
        self.assertEqual(self.authorized_client.get(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id, 'note_id': uuid.uuid4()})
        ).status_code, 404)

        # Авторизованный пользователь читает запись из несуществующего дневника
        self.assertEqual(self.authorized_client.get(
            reverse('get_note_detail',
                    kwargs={'diary_id': uuid.uuid4(), 'note_id': uuid.uuid4()})
        ).status_code, 404)

        # Метод PATCH
        # Авторизованный пользователь пытается изменить запись в дневнике
        self.assertEqual(self.authorized_client.patch(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id}),
            data=json.dumps({'text': 'Dear diary, i cant find the words..'}),
            content_type='application/json'
        ).status_code, 200)

        # Авторизованный пользователь пытается изменить несуществующую запись в дневнике
        self.assertEqual(self.authorized_client.patch(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id, 'note_id': uuid.uuid4()}),
            data=json.dumps({'text': 'Dear diary, i cant find the words..'}),
            content_type='application/json'
        ).status_code, 404)

        # Авторизованный пользователь пытается изменить несуществующую запись в несуществующем
        # дневнике
        self.assertEqual(self.authorized_client.patch(
            reverse('get_note_detail',
                    kwargs={'diary_id': uuid.uuid4(), 'note_id': uuid.uuid4()}),
            data=json.dumps({'text': 'Dear diary, i cant find the words..'}),
            content_type='application/json'
        ).status_code, 404)

        # Неавторизованный пользователь пытается изменить запись в дневнике
        self.assertEqual(self.unauthorized_client.patch(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id}),
            data=json.dumps({'text': 'Dear diary, i cant find the words...'}),
            content_type='application/json'
        ).status_code, 401)

        # Авторизованный пользователь пытается изменить запись с некорректными данными
        self.assertEqual(self.authorized_client.patch(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id}),
            data=json.dumps({'text': ''}),
            content_type='application/json'
        ).status_code, 400)

        # Метод DELETE
        # Авторизованный пользователь удаляет запись в дневнике
        self.assertEqual(self.authorized_client.delete(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id})
        ).status_code, 204)

        # Авторизованный пользователь удаляет несуществующую запись в дневнике
        self.assertEqual(self.authorized_client.delete(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id, 'note_id': uuid.uuid4()})
        ).status_code, 404)

        # Авторизованный пользователь удаляет несуществующую запись из несуществующего дневника
        self.assertEqual(self.authorized_client.delete(
            reverse('get_note_detail',
                    kwargs={'diary_id': uuid.uuid4(), 'note_id': uuid.uuid4()})
        ).status_code, 404)

        # Неавторизованный пользователь удаляет запись в дневнике
        self.assertEqual(self.unauthorized_client.delete(
            reverse('get_note_detail',
                    kwargs={'diary_id': self.test_diary_public.id,
                            'note_id': self.test_note_public_diary.id})
        ).status_code, 401)
