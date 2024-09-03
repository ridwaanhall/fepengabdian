from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import requests
import json
from requests.exceptions import ChunkedEncodingError, Timeout, RequestException
from datetime import datetime, timedelta
import calendar, time

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

    max_retries = 3  # Number of retries
    retry_delay = 2  # Delay between retries in seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            admin_data = response.json()
            return admin_data
        except ChunkedEncodingError:
            print(f"ChunkedEncodingError encountered. Retrying ({attempt + 1}/{max_retries})...")
            time.sleep(retry_delay)
            continue
        except Timeout:
            print("Request timed out. Please try again later.")
            messages.error(request, "Request timed out. Please try again later.")
            return None
        except RequestException as e:
            print(f"Request failed: {e}")
            messages.error(request, f"Request failed: {e}")
            return None

    messages.error(request, "Failed to retrieve admin data after multiple attempts.")
    return None

# dashboard
def dashboard(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    # Default to this month
    today = datetime.today()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = request.GET.get('end_date', today.replace(day=last_day).strftime('%Y-%m-%d'))

    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/kegiatan?start_date={start_date}&end_date={end_date}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if isinstance(response_data, dict) and response_data.get("detail") == "No kegiatan found":
            kegiatan_list = []
        else:
            kegiatan_list = response_data
    else:
        kegiatan_list = []
    
    print(response.status_code)
    print(response.text)
    
    context = {
        'admin_data': admin_data,
        'kegiatan_list': kegiatan_list,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'dashboard.html', context)


# pamong
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

        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            files = {'file': (foto.name, foto.read(), foto.content_type)}
        else:
            files = None

        api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/pamong/'
        data = {'pamong': json.dumps(pamong_data)}

        if files:
            response = requests.post(api_url, files=files, data=data, headers={'Accept': 'application/json'})
        else:
            response = requests.post(api_url, data=data, headers={'Accept': 'application/json'})

        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("Response JSON:", response.json())

        if response.status_code == 201:
            messages.success(request, 'Pamong berhasil ditambahkan!')
            return redirect('list-pamong')
        else:
            error_message = response.json().get('detail', 'Unknown error')
            messages.error(request, error_message)
            return render(request, 'tambah-pamong.html', context)

    return render(request, 'tambah-pamong.html', context)

def list_pamong(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/pamong'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        pamong_list = response.json()
    else:
        pamong_list = []
    
    context = {
        'admin_data': admin_data,
        'pamong_list': pamong_list
    }
    return render(request, 'list-pamong.html', context)

def detail_edit_pamong(request, pamong_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/pamong/{pamong_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    if request.method == 'GET':
        # Fetch the current pamong details to display
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            pamong_data = response.json()
            context = {
                'pamong': pamong_data,
                'admin_data': admin_data
            }
            return render(request, 'detail-edit-pamong.html', context)
        else:
            messages.error(request, 'Failed to retrieve pamong details.')
            return redirect('list-pamong')

    elif request.method == 'POST':
        # Handle form submission to update pamong details
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

        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            files = {'file': (foto.name, foto.read(), foto.content_type)}
        else:
            files = None

        data = {'pamong': json.dumps(pamong_data)}

        try:
            if files:
                response = requests.put(api_url, files=files, data=data, headers=headers)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.put(api_url, data=json.dumps(pamong_data), headers=headers)

            if response.status_code == 200:
                messages.success(request, 'Pamong berhasil diperbarui!')
                return redirect('list-pamong')
            else:
                try:
                    error_message = response.json().get('detail', 'Unknown error')
                except ValueError:
                    error_message = response.text  # Fallback to plain text in case of a non-JSON response
                messages.error(request, error_message)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return render(request, 'detail-edit-pamong.html', {'pamong': pamong_data, 'admin_data': admin_data})

def hapus_pamong(request, pamong_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    access_token = request.session.get('access_token')
    
    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/pamong/{pamong_id}'
    print(f"API URL: {api_url}")
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(api_url, headers=headers)
    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {response.text}")

    if response.status_code == 204:
        messages.success(request, 'Pamong berhasil dihapus!')
        return redirect('list-pamong')
    else:
        error_message = response.json().get('detail', 'Unknown error')
        messages.error(request, error_message)
        return redirect('list-pamong')
    

# user
def tambah_user(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    context = {
        'admin_data': admin_data
    }

    if request.method == 'POST':
        user_data = {
            "nip": request.POST.get('nip'),
            "username": request.POST.get('username'),
            "password": request.POST.get('password'),
            "email": request.POST.get('email')
        }

        api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/auth/users'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, json=user_data, headers=headers)

        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)

        if response.status_code == 201:
            messages.success(request, 'User berhasil ditambahkan!')
            return redirect('list-user')
        else:
            error_message = response.json().get('detail', 'Unknown error')
            messages.error(request, error_message)
            return render(request, 'tambah-user.html', context)

    return render(request, 'tambah-user.html', context)

def list_user(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/users'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        user_list = response.json()
    else:
        user_list = []
        
    print(user_list)
    
    context = {
        'admin_data': admin_data,
        'user_list': user_list
    }
    return render(request, 'list-user.html', context)

def detail_edit_user(request, user_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/users/{user_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    if request.method == 'GET':
        # Fetch the current user details to display
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            context = {
                'user': user_data,
                'admin_data': admin_data
            }
            return render(request, 'detail-edit-user.html', context)
        else:
            messages.error(request, 'Failed to retrieve user details.')
            return redirect('list-user')

def hapus_user(request, user_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    access_token = request.session.get('access_token')
    
    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/users/{user_id}'
    print(f"API URL: {api_url}")
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(api_url, headers=headers)
    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {response.text}")

    if response.status_code == 204:
        messages.success(request, 'User berhasil dihapus!')
        return redirect('list-user')
    else:
        error_message = response.json().get('detail', 'Unknown error')
        messages.error(request, error_message)
        return redirect('list-user')


# kegiatan
def list_kegiatan(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')

    # Default to this month
    today = datetime.today()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = request.GET.get('end_date', today.replace(day=last_day).strftime('%Y-%m-%d'))

    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/kegiatan?start_date={start_date}&end_date={end_date}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if isinstance(response_data, dict) and response_data.get("detail") == "No kegiatan found":
            kegiatan_list = []
        else:
            kegiatan_list = response_data
    else:
        kegiatan_list = []
    
    print(response.status_code)
    print(response.text)
    
    context = {
        'admin_data': admin_data,
        'kegiatan_list': kegiatan_list,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'list-kegiatan.html', context)

def detail_edit_kegiatan(request, kegiatan_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    if not refresh_token(request):
        return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/admin/kegiatan/{kegiatan_id}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    if request.method == 'GET':
        # Fetch the current kegiatan details to display
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            kegiatan_data = response.json()
            context = {
                'kegiatan': kegiatan_data,
                'admin_data': admin_data
            }
            return render(request, 'detail-kegiatan.html', context)
        else:
            messages.error(request, 'Failed to retrieve kegiatan details.')
            return redirect('list-kegiatan')

def tambah_kegiatan(request):
    return render(request, 'tambah-kegiatan.html')
