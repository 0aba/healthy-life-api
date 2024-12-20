from django_filters import rest_framework as filters
from user import models as user_model
from blog import models


class BasePostFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains', label='title')
    date_create = filters.DateFromToRangeFilter(label='time of writing')
    date_change = filters.DateFromToRangeFilter(label='time of change')

    class Meta:
        model = models.Post
        fields = ('title', 'date_create', 'date_change')


class AnyPostFilter(BasePostFilter):
    wrote = filters.ModelChoiceFilter(queryset=user_model.User.objects.all(), label='author')

    class Meta(BasePostFilter.Meta):
        fields = BasePostFilter.Meta.fields + ('wrote',)


class BloggerPostFilter(BasePostFilter):
    class Meta(BasePostFilter.Meta):
        fields = BasePostFilter.Meta.fields

