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
    return render(request, "buyer/pay_result.html", locals())

def pay_order(request):
    money = request.GET.get("money") #获取订单金额
    order_id = request.GET.get("order_id") #获取订单id

    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Vc4DEDDncW64jDXnuOWTWTYZt1vMT1yPCp+EvThS8De5y35rXBOHp5qgrD/XDN7d5RI5W0RxcJlXqntDStYweW1524z7AVl9sSC7AS5HoLPjK3ryd5MdvyqmvYSQaA0qahP/V77YEmrQ6xdOgmq+sQMQVXXYX7BKWCrZaoIz5++e3ga7zvwvV/tPI7D1xLrU/47Yy/5J4evDB3do+WTxF1YD02W9oV/03sZiR4yBA+rt9K8JpkRlMLb7pRVFQ3O8oM8nGvV9v9x5Pjhf62/cjibwQUpbSH5YUid2S9uT50MWii9czwozF7AN8BzCf05AzQiDwge/BO0bMNodhsiAQIDAQAB
    -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
    MIIEpQIBAAKCAQEA2Vc4DEDDncW64jDXnuOWTWTYZt1vMT1yPCp+EvThS8De5y35rXBOHp5qgrD/XDN7d5RI5W0RxcJlXqntDStYweW1524z7AVl9sSC7AS5HoLPjK3ryd5MdvyqmvYSQaA0qahP/V77YEmrQ6xdOgmq+sQMQVXXYX7BKWCrZaoIz5++e3ga7zvwvV/tPI7D1xLrU/47Yy/5J4evDB3do+WTxF1YD02W9oV/03sZiR4yBA+rt9K8JpkRlMLb7pRVFQ3O8oM8nGvV9v9x5Pjhf62/cjibwQUpbSH5YUid2S9uT50MWii9czwozF7AN8BzCf05AzQiDwge/BO0bMNodhsiAQIDAQABAoIBAQCOiA9eob5nonubyNIvBivUl5T/aKp6DUT0Rh2mCugRSOwlidYasvLYS6WoDbF54t1On3Vq2Ct2mLTn7uJh55Junlm7616royKqQVdmtvY8FydLp+dg3KMiyTKNK2DvnsPKm3HRxM9v5wAlAk2lOR/jElzDICt+aaT9oMLmiir7FR8JgLbw4R2JAA+TzMbdzYcNl3wPUwZoyorUTb1GPVWrTQ0HwwYdyKZbQqGkxtcpBLWhnbVMRtP2W3b9MdRi81rVRo1pPKjH+NLEUdXaN/cybkgXwt5eAebv+YIS5RcIEYD1t0C5LLpI/1wJJrIKhbCFCXFtnm9FBq6NgHamMbB9AoGBAPhDRnuiK2AW6qCq72wc9pvuZIPZX68jOlx97mRvp/zeNS+GuTuPTlhze7Ei/azcXhN6WgTY2r8YlMhHhiT2aFWDj3Lw/h/y/5+Ostxd0oG70NMqxvhabJ9aKMUkKRKUq0BiYjf6QSR7+GL8ZCEZ/oijew8GyIXISsuQrawueWnLAoGBAOAdPJXZxDIS6KKlQ7eoQ0ut63n99Phfobub+6fCZ3y/JmxM8ZlmBQSaIdeh2VRkEAYGyKnOe/j0D9WF/hcfPNPjs4s/c1h8CPRPutR2Uz378Yi10WpKfQvSMXWUD6gdOM2D5gEYVdZWmLy71G3/LGLdbU5jKWfTs9OTj0lpqJnjAoGBAOgwk4UiAQtXo40tEcu9su/XoG6oKRN2ESlcJlANFcIsWPXgPPH1b8LOD0t2fGblm57/+Z067Ct54/0E1/NN+fqwlsNbnXFoJaenIKV1omHvtLkq8vhoKdtHyYXH8hoMrbYDzfSou7BRuddqUoOa+jH1JCzDnVtyHnIRGD1HIgrNAoGBANd8hRJ4bmLPN4ubZ/8g9IPB2FZVzsM6AGJJWrE1BRg3GxSq7upV46FHKh8Racvw4k9JGovbE+yNjuP5kBRfXrdFiw7qlVeQ+3MdbkB2/RbuNpECcTbIJG/HTPMGx/8XCdTha7fF1FLgtL9Twq942Q6+ZSknw1onfhKDIRSvWQONAoGAUuMLCC87sqO0gmFaZy+9lda3aqAMCXZh1MTYy46adA7J10Z14axdoT1NKFbZrOHl2zj/u1R0870wF8mQYiuNwaPWZnz2WgQot4Te08F4Pb7rXDc65nuRDPe9G3oGSgTsedDY8BNL5x6gMzlWZjmFgoo1zxxsCCPUGoZ3U129SyI=
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

def detail(request):
    id = request.GET.get("id")
    goods = Goods.objects.filter(id=id).first()
    return render(request,"buyer/detail.html",locals())


def base(request):
    return render(request, "buyer/base.html")
