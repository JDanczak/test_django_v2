from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    #path('', views.home, name='home'),
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('main', views.main, name='main'),

    # path('oblicz/', views.oblicz),
    # path('pomiar/', views.pomiar),
    path('add/', views.add, name="add"),
    path('result2/', views.result2),

    path('upload', views.upload, name='upload'),
    path('display', views.display, name='display'),
    path('cursor_up', views.cursor_up, name='cursor_up'),
    path('cursor_down', views.cursor_down, name='cursor_down'),
    path('cursor_left', views.cursor_left, name='cursor_left'),
    path('cursor_right', views.cursor_right, name='cursor_right'),
    path('tilt_bigger', views.tilt_bigger, name='tilt_bigger'),
    path('tilt_smaller', views.tilt_smaller, name='tilt_smaller'),
    # path('add', views.add, name='add'),
    # url(r'^external', views.external),
    # url(r'^upload', views.upload)
]