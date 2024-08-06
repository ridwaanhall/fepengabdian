from django.shortcuts import render
from django.http import HttpResponse


# check
# def index(request):
#     return HttpResponse("About page")


# auth
def login(request):
    return render(request, 'login.html')

def forgot_password(request):
    return render(request, 'forgot-password.html')


# dashboard
def dashboard(request):
    return render(request, 'dashboard.html')


# pamong
def list_pamong(request):
    return render(request, 'list-pamong.html')

def detail_edit_pamong(request):
    return render(request, 'detail-edit-pamong.html')

def tambah_pamong(request):
    return render(request, 'tambah-pamong.html')


# user
def list_user(request):
    return render(request, 'list-user.html')

def detail_edit_user(request):
    return render(request, 'detail-edit-user.html')

def tambah_user(request):
    return render(request, 'tambah-user.html')


# kegiatan
def list_kegiatan(request):
    return render(request, 'list-kegiatan.html')

def detail_edit_kegiatan(request):
    return render(request, 'detail-edit-kegiatan.html')

def tambah_kegiatan(request):
    return render(request, 'tambah-kegiatan.html')
