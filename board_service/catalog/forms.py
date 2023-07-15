from catalog.models import Product
from django.forms import ModelForm


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'image', 'price', 'category')
