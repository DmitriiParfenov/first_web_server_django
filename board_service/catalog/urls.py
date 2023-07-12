from django.urls import path
from .views import index, feedback, get_products, get_products_by_word, post_feedback


urlpatterns = [
    path('', index, name='main'),
    path('feedback/', feedback, name='feedback'),
    path('products/', get_products, name='products'),
    path('products/<str:keyword>/', get_products_by_word, name='keyword'),
    path('about/', post_feedback, name='about')
]