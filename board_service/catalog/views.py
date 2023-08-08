import datetime
import json
import os

from django.core.mail import send_mail
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from pytils.translit import slugify

from catalog.forms import ProductForm, CategoryForm, BlogForm, VersionForm, VersionBaseInlineFormSet
from catalog.models import Category, Product, Feedback, Blog, Version
from users.models import User


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
        context['versions'] = Version.objects.filter(is_active=True)

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

    # Объявление модели и формы для создания
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('catalog:product_list')

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонные переменные category со всеми объектами из модели Category и title с
        названием текущей вкладки."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        context['category'] = Category.objects.all()
        context['title'] = 'Добавление товара'

        return context

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Product могут создать только авторизованные
        пользатели, причем эти пользователи автоматически присваиваются к создаваемому объекту."""

        if form.is_valid():

            # Получение текущего авторизованного пользователя
            current_user = self.request.user

            # Если пользователь есть в базе данных Users, то произойдет создание объекта в бд, иначе — вернется форма
            # с оповещением того, что необходима авторизация. В шаблоне к текущему контроллеру кнопка "Добавить объект"
            # скрыта и доступна только авторизованным пользователям.
            if User.objects.filter(email=f'{current_user}').exists():
                self.object = form.save()
                self.object.user_product = self.request.user
                self.object.save()
            else:
                self.object = form.save(commit=False)
                return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    """Контроллер на основе шаблона product_form.html позволяет редактировать объявление по модели Product."""

    model = Product
    form_class = ProductForm
    extra_context = {
        'title': 'Изменение товара'
    }
    my_form = 'catalog/product_detail.html'

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонные переменные category со всеми объектами из модели Category, title с
        названием текущей вкладки и product_user с привязанным к текущему продукту пользователем."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        context['category'] = Category.objects.all()
        context['title'] = 'Добавление товара'
        context['product_user'] = self.object.user_product

        # Объявление вложенной формы
        VersionFormset = inlineformset_factory(Product, Version, form=VersionForm, extra=1,
                                               formset=VersionBaseInlineFormSet)

        # Добавление вложенный формы в контекст
        if self.request.method == 'POST':
            formset = VersionFormset(self.request.POST, instance=self.object)
        else:
            formset = VersionFormset(instance=self.object)

        context['formset'] = formset
        return context

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Product могут изменять только авторизованные
        пользатели, к тому же пользователи не могут изменять публикации, создателями которых они не являются."""

        # Получение привязанного пользователя к текущей публикации и вложенных форм
        context_data = self.get_context_data()
        product_user = context_data['product_user']
        formset = context_data['formset']

        with transaction.atomic():
            if form.is_valid():
                current_user = self.request.user

                # Если пользователь есть в базе данных Users и он является создателем текущей публикации, то произойдет
                # создание объекта в бд, иначе — вернется форма с оповещением о невозможности изменения чужой
                # публикации. В шаблоне к текущему контроллеру кнопка "Изменить объект" скрыта и доступна только
                # авторизованным пользователям или собственникам публикации.
                if User.objects.filter(email=f'{current_user}').exists() and current_user == product_user:
                    self.object = form.save()
                    self.object.user_product = self.request.user
                    self.object.save()
                    if formset.is_valid():
                        self.object.user_product = self.request.user
                        self.object.save()
                        formset.instance = self.object
                        formset.save()
                    else:
                        return super().form_invalid(form)
                else:
                    self.object = form.save(commit=False)
                    return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)

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
    form_class = CategoryForm
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Добавление категории'
    }

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Category могут создать только авторизованные
        пользатели, причем эти пользователи автоматически присваиваются к создаваемому объекту."""

        # Если пользователь есть в базе данных Users, то произойдет создание объекта в бд, иначе — вернется форма
        # с оповещением того, что необходима авторизация. В шаблоне к текущему контроллеру кнопка "Добавить объект"
        # скрыта и доступна только авторизованным пользователям.
        if form.is_valid():
            current_user = self.request.user
            if User.objects.filter(email=f'{current_user}').exists():
                self.object = form.save()
                self.object.user_category = self.request.user
                self.object.save()
            else:
                self.object = form.save(commit=False)
                return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)


class CategoryUpdateView(UpdateView):
    """Контроллер на основе шаблона category_form.html позволяет редактировать категорию по модели Category. При
    успешном редактировании произойдет переадресация на страницу product_list.html."""

    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Изменение категории'
    }

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонную переменную category_user с привязанным к текущей категории
        пользователем."""

        context = super().get_context_data(**kwargs)
        context['category_user'] = self.object.user_category

        return context

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Category могут изменять только авторизованные
        пользатели, к тому же пользователи не могут изменять публикации, создателями которых они не являются."""

        # Получение привязанного пользователя к текущей публикации
        context_data = self.get_context_data()
        category_user = context_data['category_user']

        if form.is_valid():
            current_user = self.request.user

            # Если пользователь есть в базе данных Users и он является создателем текущей категории, то произойдет
            # создание объекта в бд, иначе — вернется форма с оповещением о невозможности изменения чужой
            # категории. В шаблоне к текущему контроллеру кнопка "Изменить объект" скрыта и доступна только
            # авторизованным пользователям или собственникам категории.
            if User.objects.filter(email=f'{current_user}').exists() and current_user == category_user:
                self.object = form.save()
                self.object.user_category = self.request.user
                self.object.save()
            else:
                self.object = form.save(commit=False)
                return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)


class CategoryDeleteView(DeleteView):
    """Контроллер на основе шаблона category_confirm_delete.html позволяет удалять строки из модели Category.
    При успешном удалении произойдет переадресация на страницу product_list.html."""

    model = Category
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Удаление категории'
    }


class BlogCreateView(CreateView):
    """Контроллер создает форму, которая позволяет пользователю добавить публикацию на основе модели Blog. При успешном
    добавлении произойдет переадресация на страницу blog_list.html."""

    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('catalog:blog_list')
    extra_context = {
        'title': 'Создание публикации'
    }

    def form_valid(self, form):
        """Метод при успешной генерации формы создает динамически slug для публикации на основе его названия."""

        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.title)
            new_mat.save()
            current_user = self.request.user

            # Если пользователь есть в базе данных Users, то произойдет создание объекта в бд, иначе — вернется форма
            # с оповещением того, что необходима авторизация. В шаблоне к текущему контроллеру кнопка "Добавить объект"
            # скрыта и доступна только авторизованным пользователям.
            if User.objects.filter(email=f'{current_user}').exists():
                self.object = form.save()
                self.object.user_blog = self.request.user
                self.object.save()
            else:
                self.object = form.save(commit=False)
                return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)


class BlogListView(ListView):
    """Контроллер генерирует страницу blog_list.html, на которой представлены все публикации, хранящиеся в
    модели Blog. В странице есть пагинация, которая отображает до 3 публикаций на одной странице."""

    paginate_by = 3
    model = Blog
    extra_context = {
        'title': 'Блок'
    }

    def get_queryset(self):
        """Метод возвращает только те публикации, для которых поле is_active есть True."""

        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


class BlogDetailView(DetailView):
    """Контроллер генерирует страницу blog_detail.html, на которой представлена информация о конкретной публикации."""

    model = Blog

    def get_object(self, queryset=None):
        """Метод инкрементирует поле view_count на 1 для конкретной публикации при обращениий к ней. Если view_count
        равняется 100, то пользователь получит письмо на указанный электронный адрес с поздравлением."""

        # Обращение к текущему объекту модели Blog
        self.object = super().get_object(queryset)
        self.object.view_count += 1
        self.object.save()

        # Создание заголовка и тела сообщения для отправки на электронный адрес
        message = f'Поздравляем!\nВаша публикация "{self.object.title}" на сайте Catalogue набрала ' \
                  f'{self.object.view_count} просмотров!\n\n С уважением, Администрация сайта!'
        subject = 'Поздравление от сайта Catalogue'

        # Объявление получателя сообщения
        recipient = self.object.email

        # Отправка сообщения пользователю, если количество просмотров равно 100
        if self.object.view_count == 100:
            send_mail(subject, message, os.getenv('yandex_login'), (recipient,))
        return self.object

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст ключ title со значением — название текущей публикации."""

        context = super().get_context_data(**kwargs)
        blog_title = Blog.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = blog_title.title
        return context


class BlogUpdateView(UpdateView):
    """Контроллер на основе шаблона идщп_form.html позволяет редактировать публикацию по модели Blog."""

    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('catalog:blog_list')
    extra_context = {
        'title': 'Изменение блога'
    }

    def get_success_url(self):
        """Метод возвращает страницу blog_detail.html при успешном обновлении публикации."""
        return reverse('catalog:blog_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонную переменную user_blog с привязанным к текущей публикации
        пользователем."""
        context = super().get_context_data(**kwargs)
        context['user_blog'] = self.object.user_blog
        return context

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Blog могут изменять только авторизованные
        пользатели, к тому же пользователи не могут изменять публикации, создателями которых они не являются."""

        # Получение текущего авторизованного пользователя
        context_data = self.get_context_data()
        user_blog = context_data['user_blog']

        # Если пользователь есть в базе данных Users и он является создателем текущей публикации, то произойдет
        # создание объекта в бд, иначе — вернется форма с оповещением о невозможности изменения чужой
        # публикации. В шаблоне к текущему контроллеру кнопка "Изменить объект" скрыта и доступна только
        # авторизованным пользователям или собственникам публикации.
        if form.is_valid():
            current_user = self.request.user
            if User.objects.filter(email=f'{current_user}').exists() and current_user == user_blog:
                self.object = form.save()
                self.object.user_blog = self.request.user
                self.object.save()
            else:
                self.object = form.save(commit=False)
                return render(self.request, 'catalog/require_authentication.html')

        return super().form_valid(form)


class BlogDeleteView(DeleteView):
    """Контроллер на основе шаблона blog_confirm_delete.html позволяет удалять строки из модели Blog.
    При успешном удалении произойдет переадресация на страницу blog_list.html."""

    model = Blog
    success_url = reverse_lazy('catalog:blog_list')
    extra_context = {
        'title': 'Удаление публикации'
    }
