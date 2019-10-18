from django.conf import settings
from django.shortcuts import render,HttpResponse
from util import find_files

def show(request):
    list=find_files()
    return render (request, "index.html", {
        "all_info": list
    })