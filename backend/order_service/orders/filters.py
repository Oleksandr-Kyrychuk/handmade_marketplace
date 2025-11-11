from django_filters import rest_framework as filters
from .models import Order

class OrderFilter(filters.FilterSet):
    customer = filters.UUIDFilter(field_name='customer_id')
    status = filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    min_total = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_total = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['customer', 'status', 'created_after', 'created_before', 'min_total', 'max_total']
