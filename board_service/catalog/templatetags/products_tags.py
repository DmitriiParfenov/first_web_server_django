from django import template
from catalog.models import Product

register = template.Library()


@register.filter()
def product_by_keyword(keyword):
    user_object = Product.objects.filter(name__icontains=keyword)
    if user_object.exists():
        return user_object
    return False