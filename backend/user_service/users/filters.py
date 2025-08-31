from django_filters import rest_framework as filters
from .models import User

class UserFilter(filters.FilterSet):
    email = filters.CharFilter(lookup_expr='icontains')
    username = filters.CharFilter(lookup_expr='icontains')
    roles = filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    is_verified = filters.BooleanFilter()

    class Meta:
        model = User
        fields = ['email', 'username', 'roles', 'is_verified']