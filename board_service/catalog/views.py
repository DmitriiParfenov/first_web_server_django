import datetime
import json
import os

from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'catalog/index.html')


def feedback(request):
    """Контроллер обрабатывает запрос от пользователя по префиксу 'feedback/' и возвращает веб-страницу
    'feedback.html'. Эта страницу является формой обратной связи, если пользователь даст обратную связь, то
    информация будет выведена в консоль и записана в файл 'data_from_users.json'. """

    # Запись даты и времени обращения пользователя
    date_now = datetime.datetime.now()
    date_now_str = datetime.datetime.strftime(date_now, '%Y-%m-%d %H:%M')

    # Запись обратной связи от пользователя в файл и вывод на консоль
    if request.method == 'POST':
        keys = list(request.POST.keys())[1:]
        values = list(request.POST.values())[1:]
        fb_from_users = dict(zip(keys, values))
        fb_from_users['time'] = date_now_str
        print(fb_from_users)
        with open('catalog/data_from_users.json', 'a') as file:
            if os.stat('catalog/data_from_users.json').st_size == 0:
                json.dump([fb_from_users], file)
            else:
                with open('catalog/data_from_users.json', 'r') as json_file:
                    data_from_file = json.load(json_file)
                    data_from_file.append(fb_from_users)
                with open('catalog/data_from_users.json', 'w') as json_file:
                    json.dump(data_from_file, json_file)
    return render(request, 'catalog/feedback.html')
