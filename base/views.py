from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import requests
import json
from requests.exceptions import ChunkedEncodingError, Timeout, RequestException
from datetime import datetime
import calendar, time
from django.conf import settings
from django.urls import reverse


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Prepare the API request
        url = f'{settings.API_URL}/auth/admin/token'
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


def forgot_password(request):
    return render(request, 'forgot-password.html')


# get user data
def get_admin_data(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('admin-login')

    url = f'{settings.API_URL}/users/me'
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

    # Get admin data
    admin_data = get_admin_data(request)
    access_token = request.session.get('access_token')

    # Get today's date in 'YYYY-MM-DD' format
    today = datetime.today().strftime('%Y-%m-%d')

    # API URLs
    api_url = f'{settings.API_URL}/admin/kegiatan?start_date={today}&end_date={today}'
    api_url_agenda = f'{settings.API_URL}/agenda/'
    api_url_user = f'{settings.API_URL}/admin/users'
    api_url_pamong = f'{settings.API_URL}/admin/pamong'

    # Set up headers
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    # Send requests to all necessary endpoints
    response = requests.get(api_url, headers=headers)
    response_agenda = requests.get(api_url_agenda, headers=headers)
    response_user = requests.get(api_url_user, headers=headers)
    response_pamong = requests.get(api_url_pamong, headers=headers)

    if (response.status_code == 200 and response_agenda.status_code == 200 and
        response_user.status_code == 200 and response_pamong.status_code == 200):

        kegiatan_list = response.json()
        agenda_list = response_agenda.json()
        user_list = response_user.json()
        pamong_list = response_pamong.json()

        # Handle no kegiatan case
        if isinstance(kegiatan_list, dict) and kegiatan_list.get("detail") == "No kegiatan found":
            kegiatan_list = []
            total_kegiatan = 0
        else:
            total_kegiatan = len(kegiatan_list)

        # Filter agendas happening today
        total_agenda_today = 0
        for agenda in agenda_list:
            tanggal_mulai = agenda.get('tanggal_mulai', '')
            tanggal_selesai = agenda.get('tanggal_selesai', '')

            # Check if today's date is between tanggal_mulai and tanggal_selesai
            if today >= tanggal_mulai[:10] and today <= tanggal_selesai[:10]:
                total_agenda_today += 1

        # Get total users and pamong
        total_user = len(user_list)
        total_pamong = len(pamong_list)

    else:
        kegiatan_list = []
        total_kegiatan = 0
        total_agenda_today = 0
        total_user = 0
        total_pamong = 0

    # Pass data to the template
    context = {
        'admin_data': admin_data,
        'kegiatan_list': kegiatan_list,
        'total_kegiatan': total_kegiatan,
        'total_agenda_today': total_agenda_today,
        'total_user': total_user,
        'total_pamong': total_pamong,
        'start_date': today,
        'end_date': today,
    }

    return render(request, 'dashboard.html', context)


# pamong
def tambah_pamong(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
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

        api_url = f'{settings.API_URL}/pamong/'
        data = {'pamong': json.dumps(pamong_data)}

        if files:
            response = requests.post(api_url, files=files, data=data, headers={'Accept': 'application/json'})
        else:
            response = requests.post(api_url, data=data, headers={'Accept': 'application/json'})

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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/pamong'
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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/pamong/{pamong_id}'
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
            response = requests.put(api_url, files=files, data=data, headers=headers)

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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/pamong/{pamong_id}'
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(api_url, headers=headers)

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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
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

        api_url = f'{settings.API_URL}/auth/users'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, json=user_data, headers=headers)


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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/users'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        user_list = response.json()
        
        # Fetch pamong data to get names
        pamong_api_url = f'{settings.API_URL}/admin/pamong'
        pamong_response = requests.get(pamong_api_url, headers=headers)
        
        if pamong_response.status_code == 200:
            pamong_list = pamong_response.json()
            pamong_dict = {pamong['id']: pamong['nama'] for pamong in pamong_list}
            
            for user in user_list:
                user['nama'] = pamong_dict.get(user['pamong_id'], 'Unknown') 

    else:
        user_list = []
        
    
    context = {
        'admin_data': admin_data,
        'user_list': user_list
    }

    return render(request, 'list-user.html', context)

def detail_edit_user(request, user_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/users/{user_id}'
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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/users/{user_id}'
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.delete(api_url, headers=headers)

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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')

    # Default to this month
    today = datetime.today()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = request.GET.get('end_date', today.replace(day=last_day).strftime('%Y-%m-%d'))

    api_url = f'{settings.API_URL}/admin/kegiatan?start_date={start_date}&end_date={end_date}'
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

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/admin/kegiatan/{kegiatan_id}'
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

def kalender_agenda(request):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    api_url = f'{settings.API_URL}/agenda/'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if isinstance(response_data, dict) and response_data.get("detail") == "No kegiatan found":
            agenda_list = []
        else:
            agenda_list = response_data
    else:
        agenda_list = []
    
    
    context = {
        'agenda_list': agenda_list,
        'admin_data': admin_data,
        'access_token': access_token
    }
    
    return render(request, 'kalender-agenda.html', context)

def tambah_agenda(request):
    if request.method == 'POST':
        access_token = request.session.get('access_token')
        api_url = f'{settings.API_URL}/agenda/'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',  # Menyatakan bahwa kita mengirimkan data sebagai JSON
        }
        
        # Mengambil data dari form dan mengubahnya menjadi format JSON
        data = {
            'nama_agenda': request.POST.get('nama_agenda'),
            'tanggal_mulai': request.POST.get('tanggal_mulai'),
            'tanggal_selesai': request.POST.get('tanggal_selesai'),
            'tempat': request.POST.get('tempat'),
            'deskripsi': request.POST.get('deskripsi'),
        }
        
        # Kirim data sebagai JSON
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:  # Created
            messages.success(request, 'Agenda berhasil ditambahkan.')
        else:
            messages.error(request, f'Gagal menambahkan agenda: {response.text}')
        
        return redirect('kalender-agenda')
    else:
        return redirect('kalender-agenda')
    
def update_agenda(request, agenda_id):
    if request.method == 'POST':
        payload = {
            'nama_agenda': request.POST['nama_agenda'],
            'tanggal_mulai': request.POST['tanggal_mulai'],
            'tanggal_selesai': request.POST['tanggal_selesai'],
            'tempat': request.POST['tempat'],
            'deskripsi': request.POST['deskripsi']
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {request.session.get("access_token")}'
        }
        response = requests.put(
            f"{settings.API_URL}/agenda/{agenda_id}",
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            messages.success(request, "Agenda berhasil diperbarui.")
        else:
            messages.error(request, "Gagal memperbarui agenda.")

    return redirect(reverse('kalender-agenda'))

def delete_agenda(request, agenda_id):
    if 'access_token' not in request.session:
        return redirect('admin-login')

    # if not refresh_token(request):
    #     return redirect('admin-login')
    
    admin_data = get_admin_data(request)
    
    access_token = request.session.get('access_token')
    
    if request.method == 'DELETE':
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.delete(
            f"{settings.API_URL}/agenda/{agenda_id}",
            headers=headers
        )
        if response.status_code == 200:
            messages.success(request, "Agenda berhasil dihapus.")
        else:
            messages.error(request, "Gagal menghapus agenda.")

    return JsonResponse({'status': 'success' if response.status_code == 204 else 'error'})