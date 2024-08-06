from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("About page")

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
