import random
import string

from django.conf import settings
from django.contrib.auth.views import LoginView as BaseLoginView, PasswordChangeView as BasePasswordChangeView
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import LoginForm, UserRegisterForm, UserProfileForm, UserChangePasswordForm
from users.models import User


# Create your views here.
class LoginView(BaseLoginView):
    """Класс контроллер для авторизации пользователей."""
    template_name = 'users/login.html'
    form_class = LoginForm


class UserRegisterView(CreateView):
    """Класс контроллер для регистрации пользователей."""
    model = User
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('catalog:index')

    def form_valid(self, form):
        """Метод позволяет активировать только тех пользователей, которые прошли верификацию через email."""

        if form.is_valid():
            # Отключение пользователя
            self.object = form.save(commit=False)
            self.object.is_active = False

            # Генерирование ключа
            user_key = ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(20))
            self.object.user_identity = user_key
            self.object = form.save()

            # Отправка email
            send_mail(
                subject='Подтвержение регистрации на портале <Catalogue>.',
                message=f'Здравстуйте, {self.object.email}!\n Для завершения регистрации, пожалуйста, перейдите по'
                        f' ссылкe:\n\nhttp://127.0.0.1:8000/users/{self.object.pk}/{user_key}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.object.email, ]
            )

            return render(self.request, 'users/verify_registration.html')

        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Метод возвращает текущего пользователя."""
        return self.request.user

    def get_context_data(self, **kwargs):
        """Метод добавляет в контекст шаблонную переменную user с текущем пользователем."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


def verify_registration(request, user_pk, user_identity):
    """Функция контроллер активирует пользователя на сайте, если тот прошел верификацию. Для этого генерируется HTML-страница
    verify_registration.html, которая сообщает пользователю, что на указанную электронную почту отправляет инструкцию
    для верификации.
    """

    # Получени пользователя по pk
    user = User.objects.get(pk=user_pk)
    context = {
        'user': user
    }

    # Если переданный ключ совпадает с ключом пользователя в бд, то пользователь активируется на сайте.
    if user.user_identity == user_identity:
        user.is_active = True
        user.save()

    return render(request, 'users/verify_registration.html', context)


class UserProfileView(UpdateView):
    """Класс контроллер для изменения данных текущего пользователя."""
    success_url = reverse_lazy('catalog:index')
    form_class = UserProfileForm
    model = User

    def get_object(self, queryset=None):
        """Метод возвращает текущего пользователя."""
        return self.request.user


def user_reset_password(request):
    """Функция контроллер сбрасывает пароль по указанному email и генерирует новый. Новый пароль присылается
    пользователю по указанному email."""

    template_name = 'users/reset_password.html'

    if request.method == 'POST':
        # Получение email из POST-запроса
        user_email = request.POST.get('email')

        # Поиск указанного email в бд и запись результата в контекст
        user_exists = User.objects.filter(email=f'{user_email}').exists()
        context = {
            'user': user_exists
        }

        # Если указанный пользователь есть в бд, то его пароль сбрасывается генерируется новый. Новый пароль присылается
        # пользователю по указанному email.
        if user_exists:
            # Генерация пароля и присвоение его пользователю
            new_password = ''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(12))
            user = User.objects.get(email=f'{user_email}')
            user.set_password(new_password)
            user.save()

            # Отправка email пользователю с новым паролем
            send_mail(
                subject='Cброс пароля на портале <Catalogue>.',
                message=f'Здравстуйте!\n\nС вашей учетной записи поступил запрос на отправку нового пароля\n\n\n\n.'
                        f'Ваш новый пароль: {new_password}\nЕсли это не Ваш запрос, не беспокойтесь.'
                        f'Это сообщение видно только вам.'
                        f'Если это ошибка, просто войдите на сайт с Вашим новым паролем и затем измените его согласно '
                        f'вашим предпочтениям.\n\n\nС уважением, администрация портала <Catalogue>.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email, ]
            )
            return render(request, 'users/reset_password_done.html', context)

        return render(request, template_name, context)

    return render(request, 'users/reset_password.html')


class PasswordChangeView(BasePasswordChangeView):
    """Класс контроллер для изменения пароля авторизованного на сайте пользователя."""

    model = User
    form_class = UserChangePasswordForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:password_change_done')
