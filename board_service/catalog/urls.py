from django.urls import path
from .views import index, feedback


urlpatterns = [
    path('', index, name='main'),
    path('feedback/', feedback, name='feedback'),
]