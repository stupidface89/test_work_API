import json
import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import generics, viewsets

from diary.tasks import task_delete_expired_diaries
from diary.models import Diary, Note, PrivateStatus

User = get_user_model()


class TestViews(APITestCase):
    """
    Все тесты разбиты по вьехам, каждый отдельно взятый тест тестирует только одну вьюху со всеми
    реализованными методами.
    """
    def setUp(self):
        # Выключаем защиту от троттлинга
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

        # Добавляем в заголовок запросов токен авторизации
        response = self.authorized_client.post(
            reverse('token_obtain_pair'), self.user_data, format='json')
        token = response.data['access']
        self.authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Добавляем в заголовок запросов токен авторизации
        response = self.authorized_client_1.post(
            reverse('token_obtain_pair'), self.user_data_1, format='json')
        token = response.data['access']
        self.authorized_client_1.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.diary_user_public = Diary.objects.create(title='Публичный дневник пользователя',
                                                      owner_id=self.user.id,
                                                      kind=PrivateStatus.public)

        self.diary_user_private = Diary.objects.create(title='Приватный дневник пользователя',
                                                       owner_id=self.user.id,
                                                       kind=PrivateStatus.private)

        self.diary_user_1_public = Diary.objects.create(title='Публичный дневник пользователя 1',
                                                        kind=PrivateStatus.public,
                                                        owner=self.user_1)

        self.diary_user_1_private = Diary.objects.create(title='Приватный дневник пользователя 1',
                                                         kind=PrivateStatus.private,
                                                         owner=self.user_1)

    def tearDown(self) -> None:
        pass

    def test_own_diaries_list_create(self):
        """
        Тестирование вывод и создание собственных дневников.
        """
        # Читаем дневники
        response = self.authorized_client.get(reverse('diaries_list_create'))
        diaries = json.loads(response.content).get('results')
        self.assertEqual(len(diaries), 3)

        # Создаем дневники
        self.authorized_client.post(reverse('diaries_list_create'),
                                    data=json.dumps({'title': 'my second pubic diary',
                                                     'kind': PrivateStatus.public}),
                                    content_type='application/json')

        self.authorized_client.post(reverse('diaries_list_create'),
                                    data=json.dumps({'title': 'my second private diary',
                                                     'kind': PrivateStatus.private}),
                                    content_type='application/json')

        response = self.authorized_client.get(reverse('diaries_list_create'))
        diaries = json.loads(response.content).get('results')
        self.assertEqual(len(diaries), 5)

    def test_diary_list_create(self):
        """
        Тестирование отображения списка дневников, приватных и публичных.
        Публичные видят все,
        Приватные дневники видят только авторы этих дневников.
        """
        # Читаем все публичные дневники
        url = reverse('diaries_list_create')

        response = self.authorized_client.get(url).content
        count_diaries_before = json.loads(response).get('count')

        self.assertEqual(count_diaries_before, 3)

        Diary.objects.create(**{"title": "Summer and Autumn",
                                "kind": PrivateStatus.public,
                                "owner": self.user})

        Diary.objects.create(**{"title": "Summer and Autumn 2",
                                "kind": PrivateStatus.private,
                                "owner": self.user_1})

        response = self.authorized_client.get(url).content
        count_diaries_after = json.loads(response).get('count')

        self.assertNotEqual(count_diaries_before, count_diaries_after)

        # Пишем дневник и проверяем количество
        response_before = self.authorized_client.get(url).content
        count_diaries_before = json.loads(response_before).get('count')

        self.authorized_client.post(url,
                                    data=json.dumps({"title": "Else one diary", "kind": "public"}),
                                    content_type='application/json')

        response_after = self.authorized_client.get(url).content
        count_diaries_after = json.loads(response_after).get('count')
        self.assertNotEqual(count_diaries_before, count_diaries_after)

    def test_diaries_user_list(self):
        """
        Тестирование вывод дневников конкретного пользователя
        """
        response = self.authorized_client.get(reverse('user_list_diaries',
                                                      kwargs={'user_id': self.user_1.id}))

        count_before = json.loads(response.content).get('count')

        Diary.objects.create(**{"title": "Test new diary Public",
                                "kind": PrivateStatus.public,
                                "owner": self.user_1})

        Diary.objects.create(**{"title": "Test new diary Private",
                                "kind": PrivateStatus.private,
                                "owner": self.user_1})

        response = self.authorized_client.get(reverse('user_list_diaries',
                                                      kwargs={'user_id': self.user_1.id}))

        count_after = json.loads(response.content).get('count')

        self.assertNotEqual(count_before, count_after)
        self.assertEqual(count_after, 2)

    def test_diary_retrieve_update_destroy(self):
        """
        Тестирование чтение, изменения и удаления дневника
        """

        # Урлы на дневники пользователя user
        public_diary_user_url = reverse('get_diary_detail',
                                        kwargs={'diary_id': self.diary_user_public.id})

        private_diary_user_url = reverse('get_diary_detail',
                                         kwargs={'diary_id': self.diary_user_private.id})

        # Урлы на дневники пользователя user_1
        public_diary_user_1_url = reverse('get_diary_detail',
                                          kwargs={'diary_id': self.diary_user_1_public.id})

        private_diary_user_1_url = reverse('get_diary_detail',
                                           kwargs={'diary_id': self.diary_user_1_private.id})

        # Пользователь user_1 открывает свой публичный дневник public_user_1
        self.assertEqual(
            json.loads(self.authorized_client_1.get(public_diary_user_1_url).content).get('title'),
            self.diary_user_1_public.title
        )

        # Пользователь user открывает чужой публичный дневник public_user_1
        self.assertEqual(
            json.loads(self.authorized_client.get(public_diary_user_1_url).content).get('title'),
            self.diary_user_1_public.title
        )

        # Пользователь user открывает чужой приватный дневник private_user_1
        self.assertEqual(
            self.authorized_client.get(private_diary_user_1_url).status_code, 404
        )

        # Пользователь user изменяет свой публичный дневник
        title_1 = 'About story public EDITED'
        title_2 = 'About story private EDITED'

        self.authorized_client.patch(public_diary_user_url,
                                     data=json.dumps({'title': title_1}),
                                     content_type='application/json')

        changed_title = json.loads(
            self.authorized_client.get(public_diary_user_url).content).get('title')
        self.assertEqual(changed_title, title_1)

        # Пользователь user изменяет свой приватный дневник
        self.authorized_client.patch(private_diary_user_url,
                                     data=json.dumps({'title': title_2}),
                                     content_type='application/json')

        changed_title = json.loads(
            self.authorized_client.get(private_diary_user_url).content).get('title')
        self.assertEqual(changed_title, title_2)

        # --------------------------------------------------
        # Пользователь user изменяет чужой публичный дневник
        title_1 = 'About story public EDITED 1'
        title_2 = 'About story private EDITED 2'

        self.authorized_client.patch(public_diary_user_1_url,
                                     data=json.dumps({'title': title_1}),
                                     content_type='application/json')

        changed_title = json.loads(
            self.authorized_client.get(public_diary_user_url).content).get('title')
        self.assertNotEqual(changed_title, title_1)

        # Пользователь user изменяет чужой приватный дневник
        self.authorized_client.patch(private_diary_user_1_url,
                                     data=json.dumps({'title': title_2}),
                                     content_type='application/json')

        self.assertEqual(self.authorized_client.get(private_diary_user_1_url).status_code, 404)

        self.assertNotEqual(
            json.loads(self.authorized_client_1.get(private_diary_user_1_url).content).get('title'),
            title_2
        )

        # ------------------------------------------------
        # Пользователь user удаляет свой публичный дневник
        self.assertEqual(self.authorized_client.get(public_diary_user_url).status_code, 200)
        self.authorized_client.delete(public_diary_user_url)
        self.assertEqual(self.authorized_client.get(public_diary_user_url).status_code, 404)

        # Пользователь user удаляет свой приватный дневник
        self.assertEqual(self.authorized_client.get(private_diary_user_url).status_code, 200)
        self.authorized_client.delete(private_diary_user_url)
        self.assertEqual(self.authorized_client.get(private_diary_user_url).status_code, 404)

        # Пользователь user удаляет чужой публичный дневник
        self.assertEqual(self.authorized_client.get(public_diary_user_1_url).status_code, 200)
        self.authorized_client.delete(public_diary_user_1_url)
        self.assertEqual(self.authorized_client.get(public_diary_user_1_url).status_code, 200)

        # Пользователь user удаляет чужой приватный дневник
        self.assertEqual(self.authorized_client_1.get(private_diary_user_1_url).status_code, 200)
        self.authorized_client.delete(private_diary_user_1_url)
        self.assertEqual(self.authorized_client_1.get(private_diary_user_1_url).status_code, 200)

    def test_note_list_create(self):
        """
        Тестирование вывода списка записей, создание записей
        """
        url_public = reverse('notes_list', kwargs={'diary_id': self.diary_user_public.id})
        url_private = reverse('notes_list', kwargs={'diary_id': self.diary_user_private.id})

        count_public_before = json.loads(
            (self.authorized_client.get(url_public)).content).get('count')

        count_private_before = json.loads(
            (self.authorized_client.get(url_private)).content).get('count')

        # Пользователь создает запись в публичном дневнике
        self.authorized_client.post(url_public,
                                    data=json.dumps({'text': 'Some note in public diary'}),
                                    content_type='application/json')

        # Пользователь создает запись в приватном дневнике
        self.authorized_client.post(url_private,
                                    data=json.dumps({'text': 'Some note in private diary'}),
                                    content_type='application/json')

        response_public = json.loads(self.authorized_client.get(url_public).content)
        response_private = json.loads(self.authorized_client.get(url_private).content)

        count_public_after = json.loads(
            (self.authorized_client.get(url_public)).content).get('count')

        count_private_after = json.loads(
            (self.authorized_client.get(url_private)).content).get('count')

        # Сравниваем количество до создания и после
        self.assertNotEqual(count_public_before, count_public_after)
        self.assertNotEqual(count_private_before, count_private_after)

        self.assertEqual(
            response_public.get('results')[0].get('text'), 'Some note in public diary')

        self.assertEqual(
            response_private.get('results')[0].get('text'), 'Some note in private diary')

    def test_note_retrieve_update_destroy(self):
        """
        Тестирование чтение, изменения и удаления конкретной записи в дневнике
        """

        diary_user_1_public = Diary.objects.create(title='Публичный дневник',
                                                   owner_id=self.user_1.id,
                                                   kind='public')

        diary_user_1_private = Diary.objects.create(title='Приватный дневник_1',
                                                    owner_id=self.user_1.id,
                                                    kind='private')

        note_user_1_public_diary = Note.objects.create(text='Запись в публичном дневнике',
                                                       diary_id=diary_user_1_public.id)

        note_user_1_private_diary = Note.objects.create(text='Запись в приватном дневнике',
                                                        diary_id=diary_user_1_private.id)

        note_user_public_diary = Note.objects.create(text='Запись в публичном дневнике',
                                                     diary_id=self.diary_user_public.id)

        note_user_private_diary = Note.objects.create(text='Запись в приватном дневнике',
                                                      diary_id=self.diary_user_private.id)

        # Пользователь читает свои записи в приватном и публичном дневниках
        response_own_public_note = self.authorized_client.get(
            reverse('get_note_detail', kwargs={'diary_id': note_user_public_diary.diary_id,
                                               'note_id': note_user_public_diary.id}))

        response_own_private_note = self.authorized_client.get(
            reverse('get_note_detail', kwargs={'diary_id': note_user_private_diary.diary_id,
                                               'note_id': note_user_private_diary.id}))

        # Пользователь читает записи в чужом приватном и публичном дневниках
        response_someone_public_note = self.authorized_client.get(
            reverse('get_note_detail', kwargs={'diary_id': note_user_1_public_diary.diary_id,
                                               'note_id': note_user_1_public_diary.id}))

        response_someone_private_note = self.authorized_client.get(
            reverse('get_note_detail', kwargs={'diary_id': note_user_1_private_diary.diary_id,
                                               'note_id': note_user_1_private_diary.id}))

        # Пользователь читает запись в своем публичном дневнике
        self.assertEqual(
            json.loads(response_own_public_note.content).get('text'), note_user_public_diary.text
        )

        # Пользователь читает запись в своем приватном дневнике
        self.assertEqual(
            json.loads(response_own_private_note.content).get('text'), note_user_private_diary.text
        )

        # Пользователь читает запись в чужом публичном дневнике
        self.assertEqual(
            json.loads(response_someone_public_note.content).get('text'), note_user_1_public_diary.text
        )

        # Пользователь читает запись в чужом приватном дневнике
        self.assertEqual(response_someone_private_note.status_code, 404)

    def test_expired_diaries_deleted(self):
        """
        Проверка функции find_and_delete_old_diaries(),
        Должны удаляться дневники, после наступления последующего дня, после
        того, который указан в поле expiration модели diary
        """
        # Создаём дневник с сегодняшней датой, после выполнения функции
        # очистки старых дневников, количество дневников не должно изменится

        count_diaries_before_create = Diary.objects.all().count()
        future_date = datetime.datetime.today().date() + datetime.timedelta(days=1)
        self.test_diary_expiration = Diary.objects.create(
            title='Дневник для тестирования expiration',
            owner_id=self.user.id,
            kind='private', expiration=future_date)

        count_diaries_after_create = Diary.objects.all().count()

        # Проверяем что количество дневник изменилось
        self.assertNotEqual(count_diaries_before_create, count_diaries_after_create)

        # Запускаем функцию удаления старых дневников, количество дневников
        # не должно изменится
        task_delete_expired_diaries()

        count_diaries_after_cleaning = Diary.objects.all().count()
        self.assertEqual(count_diaries_after_cleaning, count_diaries_after_create)

        # Создаём дневник с прошедшей датой, после выполнения функции
        # очистки старых дневников, количество дневников должно изменится

        count_diaries_before_create = Diary.objects.all().count()
        past_date = datetime.datetime.today().date() - datetime.timedelta(days=1)
        self.test_diary_expiration = Diary.objects.create(
            title='Дневник для тестирования прошедшей даты expiration',
            owner_id=self.user.id,
            kind=PrivateStatus.private, expiration=past_date)

        count_diaries_after_create = Diary.objects.all().count()

        # Проверяем что количество дневник изменилось
        self.assertNotEqual(count_diaries_before_create, count_diaries_after_create)

        # Запускаем функцию удаления старых дневников, количество дневников
        # должно изменится
        task_delete_expired_diaries()

        count_diaries_after_cleaning = Diary.objects.all().count()

        self.assertNotEqual(count_diaries_after_create, count_diaries_after_cleaning)
