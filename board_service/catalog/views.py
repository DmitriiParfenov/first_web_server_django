import datetime
import json
import os

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.edit import CreateView

from catalog.models import Category, Product, Feedback
from .forms import ProductForm


# Create your views here.
def index(request):
    """Контроллер возвращает пользователю главную страницу сервиса, где показаны 5 последних объявлений по дате."""

    object_list = Product.objects.all().order_by('-published')[0:5]
    context = {
        'object_list': object_list,
        'title': 'Catalogue'
    }
    return render(request, 'catalog/index.html', context)


def feedback(request):
    """Контроллер обрабатывает запрос от пользователя по префиксу 'feedback/' и возвращает веб-страницу
    'feedback.html'. Эта страница является формой обратной связи, если пользователь даст обратную связь, то
    информация будет выведена в консоль, записана в файл 'data_from_users.json' и добавлена на страницу about_as/. """

    # Запись даты и времени обращения пользователя
    date_now = datetime.datetime.now()
    date_now_str = datetime.datetime.strftime(date_now, '%Y-%m-%d %H:%M')

    if request.method == 'POST':
        keys = list(request.POST.keys())[1:]
        values = list(request.POST.values())[1:]

        # Создание строки в модели Feedback
        fb_from_user = Feedback.objects.create(
            first_name=values[0],
            last_name=values[1],
            email=values[2],
            phone=values[3],
            country=values[4],
            message=values[5]
        )

        # Запись обратной связи от пользователя в файл
        fb_from_users = dict(zip(keys, values))
        print(fb_from_users)
        fb_from_users['time'] = date_now_str
        with open('catalog/data_from_users.json', 'a') as file:
            if os.stat('catalog/data_from_users.json').st_size == 0:
                json.dump([fb_from_users], file)
            else:
                with open('catalog/data_from_users.json', 'r') as json_file:
                    data_from_file = json.load(json_file)
                    data_from_file.append(fb_from_users)
                with open('catalog/data_from_users.json', 'w') as json_file:
                    json.dump(data_from_file, json_file)
    context = {
        'title': 'Catalogue: обратная связь'
    }
    return render(request, 'catalog/feedback.html', context)


def get_products(request):
    """Контроллер обрабатывает запрос от пользователя по префиксу 'products/' и возвращает веб-страницу
    'all_products.html'. Эта страница отображает все имеющиеся в базе данных объявления с продуктами, а также
    ранжирует все продукты по категориям. Добавлен функционал поиска продукта по названию."""

    # Все продукты и категории
    all_products = Product.objects.all().order_by('-published')
    categories = Category.objects.all()

    # Поиск продукта по слову, переданному от пользователя
    if request.method == 'POST':
        word = request.POST.get('keyword')
        if word:
            return get_products_by_word(request, word)

    # Создание пагинатора
    paginator = Paginator(all_products, 5)

    # Выборка страниц
    if 'page' in request.GET:
        page_number = request.GET.get('page')
    else:
        page_number = 1

    # Передача страницы пагинатору
    page = paginator.get_page(page_number)
    context = {
        'products': all_products,
        'categories': categories,
        'title': 'Catalogue: все продукты',
        'page': page,
    }
    return render(request, 'catalog/all_products.html', context)


def get_products_by_word(request, keyword):
    """Контроллер обрабатывает запрос от пользователя по префиксу 'products/<str>/' и возвращает веб-страницу
    'products_by_keyword.html'. Эта страница отображает товар, найденный по ключевому слову."""

    context = {
        'keyword': keyword,
        'title': f'Catalogue: продукт {keyword}'
    }
    return render(request, 'catalog/products_by_keyword.html', context)


def post_feedback(request):
    """Контроллер обрабатывает запрос от пользователя по префиксу 'about/' и возвращает веб-страницу
    'about_as.html'. Эта страница все отзывы, полученные от пользователей. Автоматически пополняется."""

    feedback_from_user = Feedback.objects.all()
    context = {
        'fb': feedback_from_user,
        'title': 'Catalogue: о нас'
    }
    return render(request, 'catalog/about_as.html', context)


def get_product(request, product_id):
    """Контроллер динамически генерирует веб-страницу с информацией о продукте."""

    current_product = Product.objects.get(pk=product_id)
    context = {
        'title': f'Catalogue: {current_product.name}',
        'current_product': current_product,
    }

    # Поиск продукта по слову, переданному от пользователя
    if request.method == 'POST':
        word = request.POST.get('keyword')
        if word:
            return get_products_by_word(request, word)
    return render(request, 'catalog/product_card.html', context)


class ProductCreateView(CreateView):
    """Контроллер создает форму, которая позволяет пользователю добавить товар в базу данных."""

    template_name = 'catalog/create_product.html'
    form_class = ProductForm
    success_url = '../products/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context
