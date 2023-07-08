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

# Запуск

Выполните в консоли: </br>

```
python manage.py runserver
```