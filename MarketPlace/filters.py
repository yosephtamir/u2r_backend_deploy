from django_filters import rest_framework as filters
from django.db.models import Q
from MarketPlace.models import Product

class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    sub_category = filters.CharFilter(field_name='sub_category__name', lookup_expr='iexact')
    discount_price = filters.NumberFilter(field_name='discount_price', lookup_expr='lt')
    has_discount = filters.BooleanFilter(field_name='has_discount', lookup_expr='exact')
    rating = filters.NumberFilter(field_name='ave_rating', lookup_expr='gt')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gt')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lt')
    keywords = filters.CharFilter(method='filter_by_keywords')

    class Meta:
        model = Product
        fields = ['category', 'sub_category', 'discount_price', 'has_discount', 'rating', 'price_min', 'price_max', 'keywords']

    def filter_by_keywords(self, queryset, name, value):
        # Filter by product name, description, or category
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) | 
            Q(category__name__icontains=value) | 
            Q(sub_category__name__icontains=value)
        )
    
class ProductSearch(filters.FilterSet):
    searchQuery = filters.CharFilter(method='filter_by_keywords')

    class Meta:
        model = Product
        fields = ['searchQuery']

    def filter_by_keywords(self, queryset, name, value):
        # Filter by product name, description, or category
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) | 
            Q(category__name__icontains=value) | 
            Q(sub_category__name__icontains=value)
        )    