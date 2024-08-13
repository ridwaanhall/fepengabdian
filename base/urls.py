from django.urls import path
from . import views

urlpatterns = [
    # dashboard
    path('', views.dashboard, name='dashboard'),
    
    # auth
    path('login/', views.login, name='admin-login'),
    path('logout/', views.logout, name='admin-logout'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    
    # pamong
    path('list-pamong/', views.list_pamong, name='list-pamong'),
    path('detail-edit-pamong/', views.detail_edit_pamong, name='detail-edit-pamong'),
    path('tambah-pamong/', views.tambah_pamong, name='tambah-pamong'),
    
    # user
    path('list-user/', views.list_user, name='list-user'),
    path('detail-edit-user/', views.detail_edit_user, name='detail-edit-user'),
    path('tambah-user/', views.tambah_user, name='tambah-user'),
    
    # kegiatan
    path('list-kegiatan/', views.list_kegiatan, name='list-kegiatan'),
    path('detail-edit-kegiatan/', views.detail_edit_kegiatan, name='detail-edit-kegiatan'),
    path('tambah-kegiatan/', views.tambah_kegiatan, name='tambah-kegiatan'),
]