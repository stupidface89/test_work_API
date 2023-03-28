from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework.validators import ValidationError

from diary.models import Diary, Note


class DiaryListCreateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Diary
        fields = ('id', 'title', 'expiration', 'kind', 'owner', 'create_date')

    def create(self, validated_data):
        request = self.context.get('request')
        data = {**validated_data, 'owner': request.user}
        return Diary.objects.create(**data)

    def validate(self, data):
        request = self.context.get('request')
        if data.get('kind') is None:
            raise ValidationError({'kind': 'Укажите уровень приватности,'
                                           ' public или private'})

        elif (data.get('expiration') is not None and
              data.get('kind') == 'public'):
            raise ValidationError({'expiration': 'Может быть указано только у '
                                   'private дневников'})

        elif data.get('expiration') and data.get('expiration') <= datetime.now():
            not_earlier_date = datetime.now().date() + timedelta(days=1)
            raise ValidationError({'title': 'Не может быть указана прошедшая '
                                            'или текущая дата. Необходимо '
                                            'указать дату не раньше чем '
                                            f'{not_earlier_date.strftime("%d.%m.%Y")}.'})

        elif Diary.objects.filter(title=data.get('title'),
                                  owner=request.user.id).exists():

            raise ValidationError({'title': 'Дневник с таким названием у '
                                            'текущего пользователя уже есть.'})
        else:
            return data


class NoteListCreateSerializer(serializers.ModelSerializer):
    diary = serializers.StringRelatedField()
    create_date = serializers.DateTimeField(read_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        model = Note
        fields = ('id', 'diary', 'create_date', 'text')

    def create(self, validated_data):
        diary_id = self.context.get('diary_id')
        validated_data['diary_id'] = diary_id
        return self.Meta.model.objects.create(**validated_data)


class NoteRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'diary', 'create_date', 'text')


class NoteRetrieveUpdateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)

    class Meta:
        model = Note
        fields = ('id', 'create_date', 'text')


class DiaryRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    note = NoteRetrieveUpdateSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Diary
        fields = ('title', 'expiration', 'kind', 'owner', 'create_date', 'note')

    def validate(self, data):
        get_diary = Diary.objects.get(id=self.context.get('diary_id'))
        not_earlier_date = datetime.now().date() + timedelta(days=1)

        if (data.get('expiration') is not None
                and data.get('expiration') <= datetime.now().date()):
            raise ValidationError({'title': 'Не может быть указана прошедшая '
                                            'или текущая дата. Необходимо '
                                            'указать дату не раньше чем '
                                            f'{not_earlier_date.strftime("%d.%m.%Y")}.'})

        elif (data.get('expiration') is not None
                and (data.get('kind') == 'public' or get_diary.kind == 'public')):
            raise ValidationError({'expiration': 'Может быть указано только у '
                                   'private дневников'})
        else:
            return data
