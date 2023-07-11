from django.contrib import admin

from .models import Product, Category


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'published', "changed")
    list_display_links = ('name', 'category', 'price', 'published', )
    list_filter = ('category', )
    search_fields = ('name', 'description', )


@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', )
    list_display_links = ('title', )
