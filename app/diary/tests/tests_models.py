import json
import datetime

from rest_framework.test import APITestCase, APIClient
from rest_framework import generics, viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from diary.models import Diary

User = get_user_model()


class TestModels(APITestCase):
    def setUp(self) -> None:
        viewsets.GenericViewSet.throttle_classes = ()
        generics.GenericAPIView.throttle_classes = ()

        self.authorized_user = APIClient()
        self.user_data = {'email': 'Basyan2002@mail.ru', 'password': 'e12345678'}
        self.user = User.objects.create_user(**self.user_data)

        response = self.authorized_user.post(reverse('token_obtain_pair'),
                                               self.user_data, format='json')
        token = response.data['access']
        self.authorized_user.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def tearDown(self) -> None:
        pass

    def test_set_expiration_only_private(self):
        """
        Аттрибут expiration можно изменить только у приватных дневников
        """
        url = reverse('diaries_list_create')
        three_days_in_future = datetime.datetime.strftime(
                                 datetime.datetime.now() + datetime.timedelta(days=3),
                                 "%d.%m.%Y %H:%M:%S"
        )

        few_days_before = datetime.datetime.strftime(
                                 datetime.datetime.now() - datetime.timedelta(days=3),
                                 "%d.%m.%Y %H:%M:%S"
        )

        public_diary_data = {'title': 'New public Diary',
                             'kind': 'public',
                             'expiration': three_days_in_future}

        private_diary_data = {'title': 'New private Diary',
                              'kind': 'private',
                              'expiration': three_days_in_future}

        # Создаем публичный дневник с указанием expiration
        count_diaries_before = Diary.objects.filter(owner_id=self.user.id).count()

        self.authorized_user.post(url,
                                  data=json.dumps(public_diary_data),
                                  content_type='application/json')

        count_diaries_after = Diary.objects.filter(owner_id=self.user.id).count()

        self.assertEqual(count_diaries_before, count_diaries_after)

        # Создаем приватный дневник с указанием expiration
        count_diaries_before = Diary.objects.filter(owner_id=self.user.id).count()

        self.authorized_user.post(url,
                                  data=json.dumps(private_diary_data),
                                  content_type='application/json')

        count_diaries_after = Diary.objects.filter(owner_id=self.user.id).count()

        self.assertNotEqual(count_diaries_before, count_diaries_after)

        # Создаем дневник передав аттрибуту expiration прошедшее время
        private_diary_data = {'title': 'New private Diary 2',
                              'kind': 'private',
                              'expiration': few_days_before}

        count_diaries_before = Diary.objects.filter(owner_id=self.user.id).count()

        self.authorized_user.post(url,
                                  data=json.dumps(private_diary_data),
                                  content_type='application/json')

        count_diaries_after = Diary.objects.filter(owner_id=self.user.id).count()

        self.assertEqual(count_diaries_before, count_diaries_after)

