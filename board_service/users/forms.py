from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm

from catalog.forms import StyleFormMixin
from users.models import User


class LoginForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = User
        fields = ('email', 'password')


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserProfileForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'avatar', 'password', 'country', 'phone',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()


class UserChangePasswordForm(StyleFormMixin, PasswordChangeForm):
    class Meta:
        model = User
