import hashlib

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
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
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Seller.objects.filter(username=c_user).first()
            if user:
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
    """
    登陆功能，如果登陆成功，跳转到首页
    如果失败，跳转到登陆页
    """
    response = render(request,"store/login.html")
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = Seller.objects.filter(username = username).first()
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get("login_from")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("user_id", user.id) #cookie提供用户id方便其他功能查询
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

        user_id = int(request.COOKIES.get('user_id'))
        type_lists = post_data.getlist('type')
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
        for i in type_lists:
            store_type = StoreType.objects.get(id=i)
            store.type.add(store_type)
        store.save()#保存数据
    return render(request,'store/register_store.html',locals())

def base(request):
    return render(request,"store/base.html")

def logout(request):
    response = HttpResponseRedirect('/Store/login/')
    response.delete_cookie('username')
    response.delete_cookie('user_id')
    return response

def add_goods(request):
    """
    负责添加商品
    """
    if request.method == "POST":
        #获取post请求
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_store = request.POST.get("goods_store")
        goods_image = request.FILES.get("goods_image")
        #开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()
        #保存多对多数据
        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
        goods.save()
    return render(request,"store/add_goods.html")

def list_goods(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)
    if keywords:
        goods_list = Goods.objects.filter(goods_name__contains=keywords)
    else:
        goods_list = Goods.objects.all()
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    return render(request,"store/list_goods.html",{"page":page, "page_range":page_range, "keywords":keywords})
