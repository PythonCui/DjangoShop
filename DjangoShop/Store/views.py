import hashlib

from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect

from Store.models import *

# Create your views here.
def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

def user_valid(username):
    user = Seller.objects.filter(username=username).first()
    return user

def login_valid(fun):
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get("username")
        session_user = request.session.get("username")
        if username and session_user:
            user = user_valid(username)
            if user and username == session_user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Store/login/")
    return inner

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = set_password(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,"store/register.html")

def login(request):
    response = render(request, "store/login.html")
    response.set_cookie("login_form", "login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = user_valid(username)
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get("login_form")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username", username)
                    response.set_cookie("user_id", user.id)
                    request.session["username"] = username
                    return response
    return response


@login_valid
def index(request):
    user_id = request.COOKIES.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return render(request, "store/index.html", {"is_store":is_store})

def ajax_vaild(request):
    restul = {'status':'error','content':''}
    if request.method == 'GET':
        username = request.GET.get('username')
        if username:
            user = Seller.objects.filter(username=username).first()
            if user:
                restul['content'] = '用户名存在'
            else:
                restul['content'] = '用户名可以用'
                restul['status'] = 'success'
        else:
            restul['content'] = '用户名不为空'
    return JsonResponse(restul)

def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == 'POST':
        post_data = request.POST
        store_name = post_data.get('store_name')
        store_address = post_data.get('store_address')
        store_description = post_data.get('store_description')
        store_phone = post_data.get('store_phone')
        store_money = post_data.get('store_money')

        user_id = int(request.COOKIES.get('user.id'))
        type_list = post_data.get('type')
        store_logo = request.FILES.get('store_logo')

        #保存数据
        store = Store()
        store.store_name = store_name
        store.store_address = store_address
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.user_id = user_id
        store.store_logo = store_logo
        store.save()#保存数据
        for i in type_list:
            store_type = StoreType.objects.get(id=i)
            store.type.add(store_type)
        store.save()#保存数据
    return render(request,'store/register_store.html')

def base(request):
    return render(request,"store/base.html")

def logout(request):
    response = HttpResponseRedirect('/Store/login/')
    response.delete_cookie('username')
    return response

