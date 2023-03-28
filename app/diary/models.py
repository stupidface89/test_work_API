import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator

from todo.settings_components.main_config import main_config

User = get_user_model()


class PrivateStatus(models.TextChoices):
    private = 'private'
    public = 'public'


def three_days_later():
    return datetime.datetime.now() + datetime.timedelta(days=3)


class Diary(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=250, blank=False, null=False, db_index=True,
                             validators=[MinLengthValidator(3)], verbose_name="Заголовок",)

    expiration = models.DateTimeField(
        blank=True, null=True, verbose_name="Актуален до",
        default=(datetime.datetime.now() +
                 datetime.timedelta(days=main_config.DIARY_DAYS_EXPIRATION)))

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=True)

    kind = models.CharField(max_length=250, null=False, blank=False, choices=PrivateStatus.choices,
                            default=PrivateStatus.public, verbose_name="Статус приватности")

    owner = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=False,
                              blank=False, related_name='diary', verbose_name="Автор")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Diaries"
        unique_together = ('owner', 'title')


class Note(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    text = models.TextField(blank=False, null=False, validators=[MinLengthValidator(3)],
                            verbose_name="Текст",)

    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, db_index=True, related_name='note',
                              verbose_name="Дневник",)

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=True)

    def __str__(self):
        return self.text[:25] + ' ...'
