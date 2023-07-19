from django.urls import path

from .apps import CatalogConfig
from .views import IndexTemplateView, feedback, ProductListView, FeedBackListView, ProductDetailView, ProductCreateView, \
    ProductUpdateView, ProductDeleteView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView

app_name = CatalogConfig.name

urlpatterns = [
    path('', IndexTemplateView.as_view(), name='index'),
    path('feedback/', feedback, name='feedback'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('about/', FeedBackListView.as_view(), name='about_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('add_product/', ProductCreateView.as_view(), name='add_product'),
    path('update_product/<int:pk>/', ProductUpdateView.as_view(), name='update_product'),
    path('delete_product/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
    path('add_category/', CategoryCreateView.as_view(), name='add_category'),
    path('update_category/<int:pk>/', CategoryUpdateView.as_view(), name='update_category'),
    path('delete_category/<int:pk>/', CategoryDeleteView.as_view(), name='delete_category')
]
