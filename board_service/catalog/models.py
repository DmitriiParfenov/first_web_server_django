from django.db import models

NULLABLE = {'blank': True, 'null': True}


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.TextField(**NULLABLE, verbose_name='Описание')
    image = models.ImageField(upload_to='products/', **NULLABLE, verbose_name='Изображение')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата добавления')
    changed = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Изменения')
    price = models.FloatField(verbose_name='Цена')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-published']


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']