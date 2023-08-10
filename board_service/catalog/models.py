from decimal import Decimal

from django.conf import settings
from django.db import models

NULLABLE = {'blank': True, 'null': True}


# Create your models here.
class Product(models.Model):
    """
    Модель Product для сохранения определенного товара в базе данных. Поля:
    1) name — название товара, 2) description — описание товара, 3) image — иконка товара, 4) published — дата
    публикации, 5) changed — дата изменения, 6) price — цена, 7) category — категория, ссылающаяся на поле модели
    Category.
    """
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.TextField(**NULLABLE, verbose_name='Описание')
    image = models.ImageField(upload_to='products/', **NULLABLE, verbose_name='Изображение')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата добавления')
    changed = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Изменения')
    price = models.FloatField(verbose_name='Цена')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='categories',
                                 verbose_name='Категория', )
    user_product = models.ForeignKey('users.User', on_delete=models.SET_NULL, verbose_name='пользователь',
                                     **NULLABLE)
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('-published',)
        permissions = [
            (
                'set_published',
                'Can publish Продукт'
            )
        ]


class Category(models.Model):
    """
    Модель Category для сохранения категорий товаров в базе данных. Поля:
    1) category — название категории, 2) description — описание категории.
    """
    category = models.CharField(max_length=50, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    user_category = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                                      verbose_name='пользователь')

    def __str__(self):
        return f'{self.category}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('category',)


class Feedback(models.Model):
    """
    Модель Feedback для обратной связи от пользователей в базе данных. Поля:
    1) first_name — имя пользователя, 2) last_name — фамилия пользователя, 3) email — электронная почта пользователя,
    4) phone — номер телефона пользователя, 5) country — страна, откуда пользователь, 6) message — сообщение от
    пользователя, 7) publish — дата публикации.
    """
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(max_length=100, verbose_name='Электронная почта')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона', **NULLABLE)

    # Страна выбирается из выпадающего списка
    class Kinds(models.TextChoices):
        RUSSIA = 'Россия', 'Россия'
        AZERBAIJAN = 'Азербайджан', 'Азербайджан'
        ARMENIA = 'Армения', 'Армения'
        BELARUS = 'Белоруссия', 'Белоруссия'
        KAZAKHSTAN = 'Казахстан', 'Казахстан'
        KYRGYZSTAN = 'Киргизия', 'Киргизия'
        MOLDAVIA = 'Молдавия', 'Молдавия'
        TAJIKISTAN = 'Таджикистан', 'Таджикистан'
        UZBEKISTAN = 'Узбекистан', 'Узбекистан'

    country = models.CharField(max_length=150, choices=Kinds.choices, default=Kinds.RUSSIA, verbose_name='Страна')
    message = models.TextField(verbose_name='Сообщение')
    publish = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратные связи'
        ordering = ('-publish',)


class Blog(models.Model):
    title = models.CharField(max_length=50, verbose_name='Заголовок')
    slug = models.CharField(max_length=50, **NULLABLE, verbose_name='slug')
    view_count = models.IntegerField(default=0, verbose_name='Просмотры')
    content = models.TextField(**NULLABLE, verbose_name='Содержимое')
    image = models.ImageField(upload_to='blogs/', **NULLABLE, verbose_name='Превью')
    published = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=True, verbose_name='Разрешение на публикацию')
    email = models.EmailField(max_length=100, verbose_name='Электронная почта')
    user_blog = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE,
                                  verbose_name='пользователь')

    def __str__(self):
        return f'{self.title}. Просмотров ({self.view_count})'

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'
        ordering = ('-published',)


def increment_version_number():
    max_number = Version.objects.all().order_by('number').last()
    if not max_number:
        return 1.00
    return max_number.number + Decimal('0.1')


class Version(models.Model):
    class VersionName(models.TextChoices):
        NAME_DEVELOP = 'В разработке', 'В разработке'
        NAME_RELEASE = 'Выпуск в производстве', 'Выпуск в производстве'

    title = models.CharField(max_length=150, choices=VersionName.choices, default=VersionName.NAME_DEVELOP,
                             verbose_name='Название')
    number = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Номер версии',
                                 default=increment_version_number, unique=True)
    is_active = models.BooleanField(default=False, verbose_name='Активность')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='versions', verbose_name='Продукт')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'
        ordering = ('-number',)
