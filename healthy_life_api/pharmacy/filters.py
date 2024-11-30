from django_filters import rest_framework as filters
from pharmacy import models


class GoodsListFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', label='name')
    type_goods = filters.ChoiceFilter(choices=models.TypeGoods.choices, label='type')
    price = filters.RangeFilter(label='price')
    in_stock = filters.BooleanFilter(method='filter_in_stock', label='in stock')

    class Meta:
        model = models.Goods
        fields = ('name', 'type_goods', 'price', 'in_stock',)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(amount_in_stock__gt=0)
        return queryset.filter(amount_in_stock=0)

