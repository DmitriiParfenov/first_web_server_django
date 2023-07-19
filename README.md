# first_web_server_django

First_web_server_django — это проект, который представляет собой простенький веб-сервер, написанный на фреймворке Django
с генерацией HTML-страницы с формой обратной связи. В коде используются библиотеки: `json`, `django`, `os`, `datetime`


# Клонирование репозитория

Выполните в консоли: </br>

Для Windows: </br>
```
git clone git@github.com:DmitriiParfenov/first_web_server_django.git
python -m venv venv
venv\Scripts\activate
pip install poetry
poetry install
```

Для Linux: </br>
```
git clone git@github.com:DmitriiParfenov/first_web_server_django.git
cd first_web_server_django.git
python3 -m venv venv
source venv/bin/activate
curl -sSL https://install.python-poetry.org | python3
poetry install
```
# Работа с переменными окружения

- Установите адрес электронный почты [yandex](https://mail.yandex.ru/) в переменную окружения: `yandex_login`.
- Установите пароль для работы с приложением SMTP [yandex](https://id.yandex.ru/security/app-passwords) в переменную окружения: `yandex_password_smtp`.
- Установите пароль для работы с базой данных `postgresql` для пользователя `postgres` в переменную окружения: `password`.

# Запуск

Выполните в консоли: </br>

```
python manage.py runserver
```