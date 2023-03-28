import django_filters
from django_filters.filters import (ChoiceFilter,
                                    CharFilter,
                                    DateRangeFilter,
                                    DateFromToRangeFilter)

from diary.models import Note, Diary, PrivateStatus


class DiariesUserFilter(django_filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='contains')
    kind = ChoiceFilter(field_name='kind', choices=PrivateStatus.choices, lookup_expr='exact')
    expiration = DateRangeFilter()

    class Meta:
        model = Diary
        fields = ['title', 'expiration', 'kind']


class DiariesFilter(django_filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='contains')
    kind = ChoiceFilter(field_name='kind', choices=PrivateStatus.choices, lookup_expr='exact')
    owner = CharFilter(field_name='owner__email', lookup_expr='contains')
    expiration = DateFromToRangeFilter()
    create_date = DateFromToRangeFilter()

    class Meta:
        model = Diary
        fields = ['title', 'expiration', 'kind', 'owner', 'create_date']


class NoteFilter(django_filters.FilterSet):
    text = CharFilter(field_name='text', lookup_expr='contains')
    create_date = DateFromToRangeFilter()

    class Meta:
        model = Note
        fields = ['text', 'create_date']
