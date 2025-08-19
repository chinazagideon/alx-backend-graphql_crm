import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')

    phone_pattern = django_filters.CharFilter(field_name='phone', lookup_expr='startswith')

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'phone_pattern']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.RangeFilter()
    stock = django_filters.RangeFilter()

    low_stock = django_filters.NumberFilter(field_name='stock', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'low_stock']

class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    total_amount = django_filters.RangeFilter()
    
    class Meta:
        model = Order
        fields = ['customer_name', 'product_name', 'total_amount', 'order_date']