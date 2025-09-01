from django_filters import rest_framework as filters
from .models import User
from django.utils.timezone import now

class UserFilter(filters.FilterSet):
    email = filters.CharFilter(lookup_expr='icontains')
    username = filters.CharFilter(lookup_expr='icontains')
    roles = filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    is_verified = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name='date_joined', lookup_expr='gte')  # Додано
    created_before = filters.DateTimeFilter(field_name='date_joined', lookup_expr='lte')  # Додано

    class Meta:
        model = User
        fields = ['email', 'username', 'roles', 'is_verified', 'created_after', 'created_before']