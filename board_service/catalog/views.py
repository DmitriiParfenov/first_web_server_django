import datetime
import json
import os

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from pytils.translit import slugify

from catalog.forms import ProductForm, CategoryForm, BlogForm, VersionForm, VersionBaseInlineFormSet, PublishProductForm
from catalog.models import Category, Product, Feedback, Blog, Version
from catalog.services import get_cached_categories


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
        context['object_list'] = Product.objects.filter(is_published=True).order_by('-published')[0:5]
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

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_published=True)
        return queryset

    def get_context_data(self, *args, **kwargs):
        """Метод добавляет в context ключ categories, значение которого — это все объекты модели Category, и ключ
        title со значением названия текущей вкладки."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(*args, **kwargs)

        # Обновление контекста
        context['categories'] = get_cached_categories()
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


class ModerateProductList(PermissionRequiredMixin, ListView):
    """Контроллер генерирует страницу moderate_products.html, на которой представлены все объявления, требующие
    модерацию со стороны пользователя с необходимыми правами."""

    model = Product
    template_name = 'catalog/moderate_products.html'
    paginate_by = 5
    permission_required = 'catalog.set_published'
    extra_context = {
        'title': 'Модерация продуктов'
    }

    def get_queryset(self):
        """Метод возвращает объекты модели Product, у которых статус is_published = False."""
        return super().get_queryset().filter(is_published=False)


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


class ProductCreateView(LoginRequiredMixin, CreateView):
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
        context['categories'] = get_cached_categories()
        context['title'] = 'Добавление товара'

        return context

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Product могут создать только авторизованные
        пользатели, причем эти пользователи автоматически присваиваются к создаваемому объекту."""

        if form.is_valid():
            self.object = form.save()
            self.object.user_product = self.request.user
            self.object.save()

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер на основе шаблона product_form.html позволяет редактировать объявление по модели Product."""

    model = Product
    form_class = ProductForm
    extra_context = {
        'title': 'Изменение товара'
    }
    my_form = 'catalog/product_detail.html'

    def get_object(self, queryset=None):
        """Если текущий пользователь — это создатель публикации или пользователь с расширенными правами
        для редактирования, то вернется текущий объект, иначе — ошибка 404."""

        self.object = super().get_object(queryset)
        current_user = self.request.user
        if current_user == self.get_context_data()['product_user'] or self.request.user.has_perm(
                'catalog.change_product'):
            return self.object
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонные переменные category со всеми объектами из модели Category, title с
        названием текущей вкладки и product_user с привязанным к текущему продукту пользователем."""

        # Вызов текущего контекста, унаследованного от базового класса
        context = super().get_context_data(**kwargs)

        # Обновление контекста
        context['categories'] = get_cached_categories()
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

        # Получение вложенных форм
        context_data = self.get_context_data()
        formset = context_data['formset']

        with transaction.atomic():
            if form.is_valid():
                self.object = form.save()

                # Если текущий пользователь не персонал, то в поле user_product модели Product запишется текущий
                # пользователь, иначе — нет.
                if not self.request.user.is_staff:
                    self.object.user_product = self.request.user
                    self.object.save()
                self.object.save()
                if formset.is_valid():
                    if not self.request.user.is_staff:
                        self.object.user_product = self.request.user
                        self.object.save()
                    formset.instance = self.object
                    formset.save()
                else:
                    return super().form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        """Метод возвращает страницу product_detail.html при успешном обновлении объявления."""
        return reverse('catalog:product_detail', args=[self.object.id])


class PublishProductView(PermissionRequiredMixin, UpdateView):
    """Контроллер генерирует страницу publish_product.html, на которой осуществляется редактирование публикации."""
    model = Product
    form_class = PublishProductForm
    permission_required = 'catalog.set_published'
    template_name = 'catalog/publish_product.html'

    def get_success_url(self):
        """Метод возвращает страницу product_detail.html при успешной публикации."""
        return reverse('catalog:product_detail', args=[self.object.id])


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Контроллер на основе шаблона product_confirm_delete.html позволяет удалять строки из модели Product.
    При успешном удалении произойдет переадресация на страницу product_list.html."""

    model = Product
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Удаление товара'
    }

    def get_object(self, queryset=None):
        """Если текущий пользователь — это создатель публикации или пользователь с расширенными правами
        для удаления, то вернется текущий объект, иначе — ошибка 404."""

        self.object = super().get_object(queryset)
        current_user = self.request.user
        if current_user == self.object.user_product or self.request.user.is_superuser:
            return self.object
        else:
            raise Http404


class CategoryCreateView(PermissionRequiredMixin, CreateView):
    """Контроллер создает форму, которая позволяет пользователю добавить категорию в модель Category. При успешном
    добавлении произойдет переадресация на страницу product_list.html."""

    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('catalog:product_list')
    permission_required = 'catalog.add_category'
    extra_context = {
        'title': 'Добавление категории'
    }

    def form_valid(self, form):
        """Метод возвращает только валидную форму. Объекты в модели Category могут создать только авторизованные
        пользатели, причем эти пользователи автоматически присваиваются к создаваемому объекту."""

        if form.is_valid():
            self.object = form.save()
            self.object.user_category = self.request.user
            self.object.save()

        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер на основе шаблона category_form.html позволяет редактировать категорию по модели Category. При
    успешном редактировании произойдет переадресация на страницу product_list.html."""

    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('catalog:product_list')
    extra_context = {
        'title': 'Изменение категории'
    }

    def get_object(self, queryset=None):
        """Возвращает объект модели только в том случае, если пользователь обладает расширенными права доступа. """

        self.object = super().get_object(queryset)
        if self.request.user.is_staff:
            return self.object
        else:
            raise Http404

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
            self.object = form.save()
            if not self.request.user.is_staff:
                self.object.user_category = self.request.user
                self.object.save()
            self.object.save()

        return super().form_valid(form)


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    """Контроллер на основе шаблона category_confirm_delete.html позволяет удалять строки из модели Category.
    При успешном удалении произойдет переадресация на страницу product_list.html."""

    model = Category
    success_url = reverse_lazy('catalog:product_list')
    permission_required = 'catalog.delete_category'
    extra_context = {
        'title': 'Удаление категории'
    }


class BlogCreateView(LoginRequiredMixin, CreateView):
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
            self.object = form.save()
            self.object.user_blog = self.request.user
            self.object.save()

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


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер на основе шаблона идщп_form.html позволяет редактировать публикацию по модели Blog."""

    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('catalog:blog_list')
    extra_context = {
        'title': 'Изменение блога'
    }

    def get_object(self, queryset=None):
        """Возвращает объект модели только в том случае, если пользователь обладает расширенными права доступа
        или сам является создателем блога. """

        self.object = super().get_object(queryset)
        current_user = self.request.user
        if current_user == self.object.user_blog or self.request.user.has_perm('catalog.change_blog'):
            return self.object
        else:
            raise Http404

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

        if form.is_valid():
            self.object = form.save()
            if not self.request.user.is_staff:
                self.object.user_blog = self.request.user
                self.object.save()
            self.object.save()

        return super().form_valid(form)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    """Контроллер на основе шаблона blog_confirm_delete.html позволяет удалять строки из модели Blog.
    При успешном удалении произойдет переадресация на страницу blog_list.html."""

    model = Blog
    success_url = reverse_lazy('catalog:blog_list')
    extra_context = {
        'title': 'Удаление публикации'
    }
