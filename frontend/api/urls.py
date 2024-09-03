from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('hello/<str:name>/', views.hello, name='hello'),
    
    # pamong
    path('list-pamong/', views.list_pamong, name='api-list-pamong'),
    path('tambah-pamong/', views.tambah_pamong, name='api-tambah-pamong'),
]
