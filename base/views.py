from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import requests


# check
# def index(request):
#     return HttpResponse("About page")


# auth
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Prepare the API request
        url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/auth/admin/token'
        payload = {
            'username': username,
            'password': password
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Send the POST request to get the access token
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            # If successful, extract the access token and refresh token
            token_data = response.json()
            access_token = token_data['access_token']

            # Store the tokens in session
            request.session['access_token'] = access_token

            # Redirect to dashboard
            return redirect('dashboard')
        else:
            # If failed, show an error message
            messages.error(request, "Login failed. Please check your username and password.")
            return redirect('admin-login')

    return render(request, 'admin-login.html')

def logout(request):
    request.session.flush()
    return redirect('admin-login')

def refresh_token(request):
    url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/auth/refresh-token'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {request.session.get("access_token")}'
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        request.session['access_token'] = token_data['access_token']
        return True
    else:
        messages.error(request, "Session expired. Please log in again.")
        return False

def forgot_password(request):
    return render(request, 'forgot-password.html')


# get user data
def get_user_data(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('admin-login')

    url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/users/me'
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        return None

# dashboard
def dashboard(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    user_data = get_user_data(request)
    
    context = {
        'user_data': user_data
    }

    return render(request, 'dashboard.html', context)


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
