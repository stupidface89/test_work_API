from diary import views as diary
from django.urls import path

urlpatterns = [
    path('',  # List public diaries or Create new own diary
         diary.DiaryListCreate.as_view({'get': 'list',
                                        'post': 'create'}),
         name='diaries_list_create'),

    path('profile/',  # List own diaries
         diary.OwnDiariesList.as_view({'get': 'list'}),
         name='user_profile'),

    path('profile/<uuid:user_id>',  # List diaries of certain user
         diary.DiariesUserList.as_view({'get': 'list'}),
         name='user_list_diaries'),

    path('<uuid:diary_id>/',  # Retrieve, Update or Destroy certain diary
         diary.DiaryRetrieveUpdateDestroy.as_view({'get': 'retrieve',
                                                   'patch': 'partial_update',
                                                   'delete': 'destroy'}),
         name='get_diary_detail'),

    path('<uuid:diary_id>/notes/',  # List notes of certain public diary or Create new own note
         diary.NoteListCreate.as_view({'get': 'list',
                                       'post': 'create'}),
         name='notes_list'),

    path('<uuid:diary_id>/notes/<uuid:note_id>',  # Retrieve, Update, or Destroy certain note of certain diary  # noqa
         diary.NoteRetrieveUpdateDestroy.as_view({'get': 'retrieve',
                                                  'patch': 'partial_update',
                                                  'delete': 'destroy'}),
         name='get_note_detail')
]
