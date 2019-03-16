from django.shortcuts import render
from django.shortcuts import HttpResponse
from housing.models import renter

# Create your views here.

# 将请求定位到index.html文件中
def index(request):
    str = 'wyw'
    str1 = renter.objects.get(username=str).email
    return render(request, 'index.html', {'name': str,'email': str1})