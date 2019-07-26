from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from Store.models import *
from Store.views import set_password

from alipay import AliPay
# Create your views here.
def login_valid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            user = Buyer.objects.filter(username=c_user).first()
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Buyer/login/")
    return inner

def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        buyer = Buyer()
        buyer.username = username
        buyer.password = set_password(password)
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect("/Buyer/login/")
    return render(request, "buyer/register.html", locals())

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    response.set_cookie("username",user.username)
                    request.session["username"] = user.username
                    response.set_cookie("user_id",user.id)
                    return response
                else:
                    return HttpResponseRedirect("/Buyer/register/")
    return render(request, "buyer/login.html")

@login_valid
def index(request):
    result_list = []
    good_type_list = GoodsType.objects.all()
    for goods_type in good_type_list:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType={
                "id":goods_type.id,
                "name":goods_type.name,
                "description":goods_type.description,
                "picture":goods_type.picture,
                "goods_list":goods_list
            }
            result_list.append(goodsType)
    return render(request,"buyer/index.html",locals())

@login_valid
def goods_list(request):
    goodsList = []
    type_id = request.GET.get("type_id")
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        goodsList = goods_type.goods_set.filter(goods_under=1)
    return render(request,"buyer/goods_list.html",locals())

def logout(request):
    response = HttpResponseRedirect("/Buyer/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response

def pay_result(request):
    """
        支付宝支付成功自动用get请求返回的参数
        #编码
        charset=utf-8
        #订单号
        out_trade_no=10002
        #订单类型
        method=alipay.trade.page.pay.return
        #订单金额
        total_amount=1000.00
        #校验值
        sign=enBOqQsaL641Ssf%2FcIpVMycJTiDaKdE8bx8tH6shBDagaNxNfKvv5iD737ElbRICu1Ox9OuwjR5J92k0x8Xr3mSFYVJG1DiQk3DBOlzIbRG1jpVbAEavrgePBJ2UfQuIlyvAY1fu%2FmdKnCaPtqJLsCFQOWGbPcPRuez4FW0lavIN3UEoNGhL%2BHsBGH5mGFBY7DYllS2kOO5FQvE3XjkD26z1pzWoeZIbz6ZgLtyjz3HRszo%2BQFQmHMX%2BM4EWmyfQD1ZFtZVdDEXhT%2Fy63OZN0%2FoZtYHIpSUF2W0FUi7qDrzfM3y%2B%2BpunFIlNvl49eVjwsiqKF51GJBhMWVXPymjM%2Fg%3D%3D&trade_no=2019072622001422161000050134&auth_app_id=2016093000628355&version=1.0&app_id=2016093000628355
        #订单号
        trade_no=2019072622001422161000050134
        #用户的应用id
        auth_app_id=2016093000628355
        #版本
        version=1.0
        #商家的应用id
        app_id=2016093000628355
        #加密方式
        sign_type=RSA2
        #商家id
        seller_id=2088102177891440
        #时间
        timestamp=2019-07-26
        """

    return render(request, "buyer/pay_result.html", locals())

def pay_order(request):
    money = request.GET.get("money") #获取订单金额
    order_id = request.GET.get("order_id") #获取订单id


    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApFRvZQNEzn5pGfKxzjzv7pCEb2gAOpPBmRv0CXtzbftnvwJ3dC9uhFpKYLDLdZ5rKv+y3s8iWCQqcY0xnn2XzloyP2n+J2c8UFpxXN+BjRDV5j3RSdPI4aFi7EbSWVgFefGrnIwTWOwmPmD3L3GkxrPgPOm6DtN7ahE5g6Xgn6BJy/mr3474jMlS47Pj6Pr4cPNW0wOysNbwsNLPjQEEEA1vTk1gKYVcPrbb9F0HQp8NEny7A20FxNRPRMrKAD9me39Gl4ZOo5EYvCfu/qHV2PzLzffuMJrJR+NU071VRLUo65phJvKlAGC4ccuzvXjcty4fydqwgZtQi6g7Ctv2ywIDAQAB
    -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEApFRvZQNEzn5pGfKxzjzv7pCEb2gAOpPBmRv0CXtzbftnvwJ3dC9uhFpKYLDLdZ5rKv+y3s8iWCQqcY0xnn2XzloyP2n+J2c8UFpxXN+BjRDV5j3RSdPI4aFi7EbSWVgFefGrnIwTWOwmPmD3L3GkxrPgPOm6DtN7ahE5g6Xgn6BJy/mr3474jMlS47Pj6Pr4cPNW0wOysNbwsNLPjQEEEA1vTk1gKYVcPrbb9F0HQp8NEny7A20FxNRPRMrKAD9me39Gl4ZOo5EYvCfu/qHV2PzLzffuMJrJR+NU071VRLUo65phJvKlAGC4ccuzvXjcty4fydqwgZtQi6g7Ctv2ywIDAQABAoIBAGGfO3HhyD13wU5F7DUd5FdwCQz51rD12BvyDD6Z1Q/wO0iw2W/vQZNk5Cyeuq/MBdRMhOFyYe/ExGYiv+hsqgNPd+xONksIPD9sC05mBNtdtgSKkstuAjdwHYlJ5WpoLRCtbgqY+GFqIKoMBqxrsbzNXRgyrXJjVjzDsMwxfci1h1m282yt+SDx9M7rMJAwjD1qO44JP/MBJfT6fA3fH2TCtY5NruuEXo5gO3qT76KF42bE8zfyi9x31nk/84ofMLn4ScHkxFPp6wY2s0LxoY1IHUIzX5m8T5mcy+VPWdAK8o3qcrqcll0uGSF0HPZdBQHG/N966TifWpCLAHDtNnECgYEA1dNAyoe5lY1hF1QHFXXD0S2MNrXBPhnp2lt5q64EGis+f8RXIq7H1+4rPVtjnzDqhncW+qS0uJz0tgjX7uUgXlMGt4FxuZj1h6OkX3vZ+TFtjWQV/OP83HAWU4m8DbTAOnTEQpmSer7dZ20SBH9ARfOWJmTOj6bEPsuyw3jE61kCgYEAxL3+zVfZxGZMZo7/bgNEv5vkNZ7jZsydFalwJbCpwLnZwAnELh/khzj+YzJXuq3wlgPzWJ4RoSL7un+gXm+XL2R2+42GkLXZY5s1ViZAnamsJUzSXeQq0hM0+M5dvEQ5D9XTGNTNV9g830e4cGYZ2LQWwbsbjLN2fRgKB0h2AsMCgYB2fyc11fecEIiQ5Ak09Fl7b9F3dExOPRAi6XTJFpvBYNu29LkRSGkJmjyuORpBW1ts/0xlxKc+dAUNaGM6ShIhE8PyKDM9Fq5i5+Ys4DcQ6Tp8E843oqU8CIXm77qeod+xxYoKGo9ZpLKQIZrNkTOuUGqShmUOqO2ymzJLL395qQKBgAIEcLhqTjFVWzMyBCx8nBfa4VwrZOmI75NpSV0ZkqQHQ9RURU6zxQQd8X3S5lNjtTPUlooyFLwyP6KJ7HsLaeFyhkXODbMuKix7SvC3M7JqKvm27/FGhanhyIlElHF5wZwH9UIr7G8aKIWhlqKQaXNvZUxXPtEShgSCWpf4hj1BAoGAAq/A/88OuF+vEnXqYrVzFKxHXwzzVGIzUkLCcg06oBaQNCo3ja87erPGJOvaCNfT/6OtYI/GhUqALIeLB2npUnNkqb2cAPies3kSFzaeTFp9cVgLr2uDzFAznQP8ck/o7mGXqiLRA3ek2h2iPaMXYiuHfHmoYGPEyUg3Edb3Z70=
    -----END RSA PRIVATE KEY-----'''

    alipay = AliPay(
        appid="2016101000652590",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    # 发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,  # 订单号
        total_amount=str(money),  # 支付金额
        subject="生鲜交易",  # 交易主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/",
    )

    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)

def base(request):
    return render(request,"buyer/base.html")
