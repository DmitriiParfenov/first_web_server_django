from django.contrib.auth.views import LogoutView, PasswordChangeDoneView
from django.urls import path

from users.apps import UsersConfig
from users.views import LoginView, UserRegisterView, UserProfileView, verify_registration, user_reset_password, \
    PasswordChangeView

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('<int:user_pk>/<slug:user_identity>/', verify_registration, name='verify_registration'),
    path('reset_password/', user_reset_password, name='reset_password'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='users/change_password_done.html'),
         name='password_change_done')
]
