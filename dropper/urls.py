from django.urls import path

from dropper import views

urlpatterns = [
    path('', views.index, name='index'),
    path('drop/<slug:drop_uuid>', views.get_drop, name='get_link')
]