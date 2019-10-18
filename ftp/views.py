import os
from django.conf import settings
from django.shortcuts import render,HttpResponse
from util import find_files

from ftp.models import PathItem,FileItem
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,StreamingHttpResponse,FileResponse

# def index(request):
#     current = ''
#     context_dic = {}
#     context_dic['current'] = current
#     ps = os.listdir(current)
#     path = []
#     file = []
#     for n in ps:
#         v = os.path.join(current, n)
#         if os.path.isdir(v):
#             p = PathItem(n, current)
#             path.append(p)
#         else:
#             f = FileItem(n, current)
#             file.append(f)
#
#     context_dic['path'] = path
#     context_dic['file'] = file
#     return render(request, 'stock_list.html', context_dic)
def index (request):
    return render(request, 'index.html')
@csrf_exempt
def file_Download(request,path,file):
    print ("request1= %s request2= %s" %(path,file))
    fileName=str(os.path.join(path,file))
    file=open(fileName,'rb')
    response=FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename='+str(fileName)
    return response
    # return render(request, 'stock_list.html')
def show_folder(request, url):
    current = url
    context_dic = {}
    context_dic['current'] = current
    ps = os.listdir(current)
    # print(ps)
    path = []
    file = []
    for n in ps:
        v = os.path.join(current, n)
        if os.path.isdir(v):
            p = PathItem(n, current)
            path.append(p)
        else:
            f = FileItem(n, current)
            file.append(f)
    # context_dic['parent'] = os.path.pardir(url)
    context_dic['path'] = path
    context_dic['file'] = file
    return render(request, 'stock_list.html', context_dic)