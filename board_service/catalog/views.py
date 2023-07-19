import datetime
import json
import os

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView

from catalog.models import Category, Product, Feedback


class IndexTemplateView(TemplateView):
    """Контроллер генерирует страницу index.html, на которой представлены 5 последних публикаций, остортированных по
    дате."""
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        """Метод добавляет в context ключ object_list, значение которого — это 5 последних публикаций, остортированных
        по дате, и ключ title со значением названия текущей вкладки."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        context['object_list'] = Product.objects.all().order_by('-published')[0:5]
        context['title'] = 'Catalogue'
        return context


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


class ProductListView(ListView):
    """Контроллер генерирует страницу product_list.html, на которой представлены все объявления и все категории.
    Добавлена пагинация, на каждой странице присутствуют до 5 объявлений. Реализован функционал по поиску товара
    по имени."""

    # Объявление переменных
    paginate_by = 5
    model = Product
    my_form = 'catalog/products_by_keyword.html'

    def get_context_data(self, *args, **kwargs):
        """Метод добавляет в context ключ categories, значение которого — это все объекты модели Category, и ключ
        title со значением названия текущей вкладки."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(*args, **kwargs)

        # Обновление контекста
        context['categories'] = Category.objects.all()
        context['title'] = 'Catalogue: все продукты'
        return context

    def post(self, request):
        """Метод генерирует шаблон products_by_keyword.html, как результат поиска товара по ключу, полученному от
         пользователя в POST-запросе."""

        word = request.POST.get('keyword')
        if word:
            return render(request, self.my_form, {'keyword': word})
        return HttpResponseRedirect(reverse_lazy('catalog:product_list'))


class FeedBackListView(ListView):
    """Контроллер генерирует страницу feedback_list.html, на которой представлены все отзывы, хранящиеся в
    модели FeedBack."""

    model = Feedback
    extra_context = {
        'title': 'Catalogue: о нас'
    }


class ProductDetailView(DetailView):
    """Контроллер генерирует страницу product_detail.html, на которой представлена информация о конкретном товаре."""

    model = Product

    def get_context_data(self, **kwargs):
        """Метод добавляет в context ключ title, значение которого — это название рассматриваемого товара."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        product_name = Product.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = f'Catalogue: {product_name.name}'
        return context


class ProductCreateView(CreateView):
    """Контроллер создает форму, которая позволяет пользователю добавить товар в базу данных."""

    # Объявление модели и полей для создание
    model = Product
    fields = ('name', 'description', 'image', 'price', 'category')
    success_url = reverse_lazy('catalog:product_list')

    # Вызов текущего контекста, унаследованного от базового класса
    def get_context_data(self, **kwargs):

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        context['category'] = Category.objects.all()
        context['title'] = 'Добавление товара'
        return context


class ProductUpdateView(UpdateView):
    """Контроллер на основе шаблона product_form.html позволяет редактировать объявление по модели Product."""

    model = Product
    fields = ('name', 'description', 'image', 'price', 'category')
    extra_context = {
        'title': 'Изменение товара'
    }

    def get_success_url(self):
        """Метод возвращает страницу product_detail.html при успешном обновлении объявления."""
        return reverse('catalog:product_detail', args=[self.object.id])


class ProductDeleteView(DeleteView):
    """Контроллер на основе шаблона product_confirm_delete.html позволяет удалять строки из модели Product.
    При успешном удалении произойдет переадресация на страницу product_list.html."""

    model = Product
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Удаление товара'
    }


class CategoryCreateView(CreateView):
    """Контроллер создает форму, которая позволяет пользователю добавить категорию в модель Category. При успешном
    добавлении произойдет переадресация на страницу product_list.html."""

    model = Category
    fields = ('category', 'description')
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Добавление категории'
    }


class CategoryUpdateView(UpdateView):
    """Контроллер на основе шаблона category_form.html позволяет редактировать категорию по модели Category. При
    успешном редактировании произойдет переадресация на страницу product_list.html."""

    model = Category
    fields = ('category', 'description')
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Изменение категории'
    }


class CategoryDeleteView(DeleteView):
    """Контроллер на основе шаблона category_confirm_delete.html позволяет удалять строки из модели Category.
    При успешном удалении произойдет переадресация на страницу product_list.html."""

    model = Category
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Удаление категории'
    }
