from django.urls import path

from users.views import UserCreate

urlpatterns = [
    path('create-user', UserCreate.as_view(), name='create_user'),
]
