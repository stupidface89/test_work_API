import datetime

from celery import shared_task

from diary.models import Diary


@shared_task
def task_delete_expired_diaries():
    """
    Функция удаляет дневники у которых показатель даты в
    поле expiration < сегодняшней даты
    """
    get_diaries = Diary.objects.filter(expiration__lt=datetime.datetime.now())
    for diary in get_diaries:
        diary.delete()
