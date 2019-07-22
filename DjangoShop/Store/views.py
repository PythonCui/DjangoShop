import hashlib

from django.shortcuts import render
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
                    request.session["username"] = username
                    return response
    return response

@login_valid
def index(request):
    username = request.COOKIES.get("username")
    user = Seller.objects.get(username=username)
    return render(request,"store/index.html")
