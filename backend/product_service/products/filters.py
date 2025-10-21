from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    sale_type = filters.ChoiceFilter(choices=Product.SALE_TYPE_CHOICES)
    is_approved = filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'sale_type', 'is_approved']
