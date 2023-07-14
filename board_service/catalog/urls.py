from django.urls import path

from .apps import CatalogConfig
from .views import index, feedback, get_products, get_products_by_word, post_feedback, get_product

app_name = CatalogConfig.name

urlpatterns = [
    path('', index, name='main'),
    path('feedback/', feedback, name='feedback'),
    path('products/', get_products, name='products'),
    path('products/<str:keyword>/', get_products_by_word, name='keyword'),
    path('about/', post_feedback, name='about'),
    path('products/<int:product_id>', get_product, name='product')
]