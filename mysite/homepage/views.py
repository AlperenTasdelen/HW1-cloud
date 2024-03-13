from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'homepage/index.html', {})

def hello(request):
    return HttpResponse("This is the about page.")

def catay(request):
    return render(request, 'homepage/catay.html', {})