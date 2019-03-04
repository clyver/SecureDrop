from django.urls import path

from drop.dropper import views

urlpatterns = [
    path('', views.index, name='index'),
]
