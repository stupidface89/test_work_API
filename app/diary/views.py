from django.http import Http404

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema

from diary import mixins as diary_mixins
from diary.models import Diary, PrivateStatus, Note
from diary.filters import DiariesUserFilter, DiariesFilter, NoteFilter
from users.permissions import IsOwnerOrReadOnlyPermission
from diary.serializers import (DiaryListCreateSerializer,
                               NoteListCreateSerializer,
                               NoteRetrieveUpdateDestroySerializer,
                               DiaryRetrieveUpdateDestroySerializer)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(description='Получение списка собственных дневников', tags=['Diary']),
)
class OwnDiariesList(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     diary_mixins.InstanceRequestInContextMixin,
                     viewsets.GenericViewSet):

    serializer_class = DiaryListCreateSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission)
    filterset_class = DiariesUserFilter  # noqa
    ordering = ('create_date',)

    def get_queryset(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            return Diary.objects.none()

        return Diary.objects.filter(owner=self.request.user).select_related('owner')


@extend_schema_view(
    list=extend_schema(description='Получение списка всех публичных дневников', tags=['Diary']),
    create=extend_schema(description='Создание нового дневника', tags=['Diary']),
)
class DiaryListCreate(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      diary_mixins.InstanceRequestInContextMixin,
                      viewsets.GenericViewSet):

    serializer_class = DiaryListCreateSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission,)
    ordering = ('create_date',)
    filterset_class = DiariesFilter # noqa

    def get_queryset(self, *args, **kwargs):
        """
        Если пользователь, от токена которого осуществляется запрос, является автором, то он также
        видит и свои приватные дневники.
        """
        q = Q(owner_id=self.request.user.id) | Q(kind=PrivateStatus.public)
        get_diaries = Diary.objects.filter(q).select_related('owner')

        if self.request.query_params.get('owner'):
            email_value = self.request.query_params.get('owner')
            get_diaries = get_diaries.filter(owner__email=email_value)

        return get_diaries


@extend_schema_view(
    list=extend_schema(description='Получение списка публичных дневников пользователя',
                       tags=['Diary'])
)
class DiariesUserList(mixins.ListModelMixin,
                      diary_mixins.InstanceRequestInContextMixin,
                      viewsets.GenericViewSet):

    serializer_class = DiaryListCreateSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission)
    filterset_class = DiariesUserFilter # noqa
    ordering = ('create_date',)

    def get_queryset(self, *args, **kwargs):
        """
        Если пользователь, от токена которого осуществляется запрос, является автором,
        то он видит все свои дневники.
        """
        if getattr(self, "swagger_fake_view", False):
            return Diary.objects.none()

        query_user = self.kwargs.get('user_id')
        get_user = get_object_or_404(User, id=query_user)

        q = Q(owner_id=get_user.id)
        if self.request.user.id != get_user.id:
            q = q & Q(kind=PrivateStatus.public)

        return Diary.objects.filter(q).select_related('owner')


@extend_schema_view(
    retrieve=extend_schema(description='Получение конкретного дневника', tags=['Diary']),
    partial_update=extend_schema(description='Изменение собственного дневника', tags=['Diary']),
    destroy=extend_schema(description='Удаление собственного дневника', tags=['Diary']),
)
class DiaryRetrieveUpdateDestroy(diary_mixins.CheckObjectPermissionsMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 diary_mixins.InstanceRequestInContextMixin,
                                 diary_mixins.SendKwargsInContextMixin,
                                 viewsets.GenericViewSet):

    serializer_class = DiaryRetrieveUpdateDestroySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission,)

    def get_object(self):
        diary_id = self.kwargs.get('diary_id')
        get_diary = get_object_or_404(
            Diary.objects.select_related('owner').prefetch_related('note'), id=diary_id)

        if get_diary.kind == PrivateStatus.private and self.request.user != get_diary.owner:
            raise Http404
        return get_diary


@extend_schema_view(
    list=extend_schema(description='Получение списка записей из дневника', tags=['Note']),
    create=extend_schema(description='Создание записи в дневнике', tags=['Note']),
)
class NoteListCreate(diary_mixins.CheckObjectPermissionsMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     diary_mixins.SendKwargsInContextMixin,
                     diary_mixins.InstanceRequestInContextMixin,
                     viewsets.GenericViewSet):

    serializer_class = NoteListCreateSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission,)
    filterset_class = NoteFilter
    ordering = ('diary',)

    def get_queryset(self):
        """
        Если пользователь, от токена которого осуществляется запрос, является автором дневника,
        то он видит записи и приватных и публичных дневников. Иначе вызываем ошибку 404
        """
        if getattr(self, "swagger_fake_view", False):
            return Note.objects.none()

        get_diary = get_object_or_404(Diary.objects.all(),
                                      id=self.kwargs.get('diary_id'))

        if get_diary.kind == PrivateStatus.private and get_diary.owner != self.request.user:
            raise Http404

        get_notes = Note.objects.filter(diary=get_diary).select_related('diary')
        return get_notes

    def perform_create(self, serializer):
        diary_id = self.get_serializer_context().get('diary_id')
        request = self.get_serializer_context().get('request')

        get_diary = get_object_or_404(Diary, id=diary_id)

        if get_diary.owner != request.user:
            raise PermissionDenied

        serializer.save()


@extend_schema_view(
    retrieve=extend_schema(description='Получение конкретной записи из дневника', tags=['Note']),
    partial_update=extend_schema(description='Изменение записи в дневнике', tags=['Note']),
    destroy=extend_schema(description='Удаление записи из дневника', tags=['Note']),
)
class NoteRetrieveUpdateDestroy(diary_mixins.CheckObjectPermissionsMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                diary_mixins.InstanceRequestInContextMixin,
                                viewsets.GenericViewSet):

    serializer_class = NoteRetrieveUpdateDestroySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission,)
    filterset_fields = ('create_date',)

    def get_object(self):
        """
        Если пользователь, от токена которого осуществляется запрос, является автором дневника,
        то он может редактировать и удалять запись. Иначе вызываем ошибку 404
        """
        get_note = get_object_or_404(Note.objects.select_related('diary'),
                                     diary=self.kwargs.get('diary_id'),
                                     id=self.kwargs.get('note_id'))

        if (get_note.diary.kind == PrivateStatus.private and
                (get_note.diary.owner != self.request.user and
                 not self.request.user.is_staff)):
            raise Http404
        return get_note
