from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import requests
import json


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
            
            # set the success message
            messages.success(request, "Login successful.")

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
def get_admin_data(request):
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
        admin_data = response.json()
        return admin_data
    else:
        return None

# dashboard
def dashboard(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    context = {
        'admin_data': admin_data
    }

    return render(request, 'dashboard.html', context)


# pamong
def list_pamong(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    # get access token
    access_token = request.session.get('access_token')
    
    api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/pamong'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'  # Menyertakan token dalam header
    }

    # Mengirim permintaan GET ke API eksternal
    response = requests.get(api_url, headers=headers)

    # Cek status code
    if response.status_code == 200:
        pamong_list = response.json()  # Mengambil data JSON dari respons
    else:
        pamong_list = []
    
    context = {
        'admin_data': admin_data,
        'pamong_list': pamong_list
    }
    return render(request, 'list-pamong.html', context)

def detail_edit_pamong(request):
    return render(request, 'detail-edit-pamong.html')


def tambah_pamong(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    context = {
        'admin_data': admin_data
    }
    if request.method == 'POST':
        # Ambil data dari form
        pamong_data = {
            "jenis_kelamin": request.POST.get('jenis_kelamin'),
            "gol_darah": request.POST.get('gol_darah'),
            "tempat_lahir": request.POST.get('tempat_lahir'),
            "pekerjaan": request.POST.get('pekerjaan'),
            "nama": request.POST.get('nama'),
            "tanggal_lahir": request.POST.get('tanggal_lahir'),
            "alamat": request.POST.get('alamat'),
            "jabatan": request.POST.get('jabatan'),
            "agama": request.POST.get('agama'),
            "nik": request.POST.get('nik'),
            "pendidikan_terakhir": request.POST.get('pendidikan_terakhir'),
            "nip": request.POST.get('nip'),
            "status_kawin": request.POST.get('status_kawin'),
            "masa_jabatan_mulai": int(request.POST.get('masa_jabatan_mulai')),
            "masa_jabatan_selesai": int(request.POST.get('masa_jabatan_selesai'))
        }

        # Periksa apakah file foto diunggah
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            files = {'file': (foto.name, foto.read(), foto.content_type)}
        else:
            files = None  # Jika tidak ada foto, set files ke None

        # Kirim data ke API eksternal
        api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/pamong/'
        data = {'pamong': json.dumps(pamong_data)}

        # Jika ada file yang diunggah, sertakan dalam permintaan
        if files:
            response = requests.post(api_url, files=files, data=data, headers={'Accept': 'application/json'})
        else:
            response = requests.post(api_url, data=data, headers={'Accept': 'application/json'})

        # Print respons untuk debugging
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Response JSON:", response.json())

        # Tangani respon dari API eksternal
        if response.status_code == 201:
            # Tambahkan pesan sukses
            messages.success(request, 'Pamong berhasil ditambahkan!')
            return redirect('list-pamong')
        else:
            # Tangani error
            error_message = response.json().get('detail', 'Unknown error')
            messages.error(request, error_message)
            return render(request, 'tambah-pamong.html', context)

    return render(request, 'tambah-pamong.html', context)


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
