from django.contrib import admin

from .models import Product, Category, Feedback


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'published', "changed")
    list_display_links = ('name', 'category', 'price', 'published', )
    list_filter = ('category', )
    search_fields = ('name', 'description', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category', )
    list_display_links = ('category', )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'country', 'message', )
    list_display_links = ('first_name', 'last_name', 'country', 'message', )
    search_fields = ('first_name', 'message')

