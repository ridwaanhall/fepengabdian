from django.http import JsonResponse
from django.shortcuts import render
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def list_pamong(request):
    url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/pamong/'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return Response(data, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def tambah_pamong(request):
    url = 'https://technological-adriena-taufiqdp-d94bbf04.koyeb.app/pamong/'
    
    try:
        response = requests.post(url, json=request.data)
        response.raise_for_status()

        data = response.json()

        return Response(data, status=response.status_code)

    except requests.exceptions.HTTPError as e:
        error_response = {
            'error': response.json() if response.content else str(e),
            'status_code': response.status_code
        }
        return Response(error_response, status=response.status_code)
    
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def index(request):
    return JsonResponse({'message': 'Welcome to API'})

@api_view(['GET'])
def hello(request, name):
    return JsonResponse({'message': f'Hello {name}'})