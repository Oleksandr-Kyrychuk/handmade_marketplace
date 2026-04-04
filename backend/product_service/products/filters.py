from django_filters import rest_framework as filters
from .models import Category, Product
from django.db.models import Avg, Q as models_Q

class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    sale_type = filters.ChoiceFilter(choices=Product.SALE_TYPE_CHOICES)
    is_approved = filters.BooleanFilter()

    # Фільтри за датою створення
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # Фільтри за середнім рейтингом
    min_rating = filters.NumberFilter(method='filter_min_rating')
    max_rating = filters.NumberFilter(method='filter_max_rating')


    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'sale_type', 'is_approved',
                  'created_after', 'created_before', 'min_rating', 'max_rating'
                  ]

    def filter_min_rating(self, queryset, name, value):
        return queryset.annotate(
            avg_rating=Avg('reviews__rating', filter=models_Q(reviews__is_approved=True))
        ).filter(avg_rating__gte=value)

    def filter_max_rating(self, queryset, name, value):
        return queryset.annotate(
            avg_rating=Avg('reviews__rating', filter=models_Q(reviews__is_approved=True))
        ).filter(avg_rating__lte=value)

class CategoryFilter(filters.FilterSet):
    parent = filters.NumberFilter(field_name='parent__id', lookup_expr='exact')
    name   = filters.CharFilter(lookup_expr='icontains')           # простий пошук за частиною назви
    search = filters.CharFilter(method='filter_search')            # повнотекстовий пошук через search_vector

    class Meta:
        model = Category
        fields = ['parent', 'name']

    def filter_search(self, queryset, name, value):
        if not value.strip():
            return queryset
        # Використовуємо існуючий GIN-індекс search_vector
        return queryset.filter(search_vector=value)


