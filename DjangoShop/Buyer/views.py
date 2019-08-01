import time

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from Store.models import *
from Store.views import set_password

from alipay import AliPay
# Create your views here.
def set_order_id(user_id,goods_id,store_id):
    time_now = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return time_now+str(user_id)+str(goods_id)+str(store_id)

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
    user_id = request.COOKIES.get("user_id")
    user = Buyer.objects.get(id=user_id)
    orders = user.order_set.filter(order_user=user_id)
    for order in orders:
        order.order_id = order.order_id
        order.goods_count = order.goods_count
        order.order_user = order.order_user
        order.order_address = order.order_address
        order.order_price = order.order_price
        order.order_status = 2
        order.save()
    carts = Cart.objects.filter(user_id=int(user_id))
    for cart in carts:
        goods = Goods.objects.get(id=cart.goods_id)
        goods.goods_number -= cart.goods_number
        goods.save()
        cart.delete()
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
    if id:
        goods = Goods.objects.filter(id=id).first()
        if goods:
            number = goods.goods_number
            return render(request,"buyer/detail.html",locals())
    return HttpResponse("未找到您指定的商品！")

def place_order(request):
    if request.method == "POST":
        # post数据
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        # cookie的数据
        user_id = request.COOKIES.get("user_id")
        # 数据库的数据
        goods = Goods.objects.get(id=goods_id)

        store_id = goods.store_id.id  # 获取商品对应的商店的id

        order = Order()
        order.order_id = set_order_id(str(user_id), str(goods_id), str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = count * goods.goods_price
        order.save()

        order_detail = OrderDetail()
        order_detail.order_id = order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count * goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image
        order_detail.save()

        detail = order.orderdetail_set.all()
        return render(request, "buyer/place_order.html", locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.orderdetail_set.all()
            return render(request, "buyer/place_order.html", locals())
        else:
            return HttpResponse("非法请求")


def cart(request):
    user_id = request.COOKIES.get("user_id")
    total = 0
    num = 0
    goods_list = Cart.objects.filter(user_id=user_id)
    num = len(goods_list)
    for goods in goods_list:
        total += goods.goods_number*goods.goods_price
        number = goods.goods_number
    if request.method == "POST":
        post_data = request.POST
        cart_data = []  # 收集前端传递过来的商品
        for k, v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id=int(v)))
        goods_count = len(cart_data)  # 提交过来的的数据总的数量
        goods_total = sum([int(i.goods_total) for i in cart_data])  # 订单的总价

        # 保存订单
        order = Order()
        order.order_id = set_order_id(user_id, goods_count, "2")
        # 订单当中有多个商品或者多个店铺，使用goods_count来代替商品id，用2代替店铺id
        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        # 保存订单详情
        # 这里的detail是购物车里的数据实例，不是商品的实例
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order  # order是一条订单数据
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()
            # order是一条订单支付页
        url = "/Buyer/place_order/?order_id=%s" % order.id
        return HttpResponseRedirect(url)

    return render(request, "buyer/cart.html", locals())

def add_cart(request):
    result = {"state": "error", "data": ""}
    if request.method == "POST":
        # request请求得到
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        # 数据库查询得到
        goods = Goods.objects.get(id=int(goods_id))
        # cookies数据
        user_id = request.COOKIES.get("user_id")

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = goods.goods_price * count
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result["state"] = "success"
        result["data"] = "商品添加成功"
    else:
        result["error"] = "请求错误"
    return JsonResponse(result)

def user_center_info(request):
    user_id = request.COOKIES.get("user_id")
    buyer = Buyer.objects.get(id=user_id)
    return render(request,"buyer/user_center_info.html",locals())

def user_center_order(request):
    time_now = time.strftime("%Y-%m-%d\t\t\t\t%H:%M:%S", time.localtime())
    user_id = request.COOKIES.get("user_id")
    goods_total = 0
    goods_list = Cart.objects.filter(user_id=user_id)
    goods_count = len(goods_list)
    for goods in goods_list:
        goods_total += goods.goods_number * goods.goods_price
        cart_data = []  # 收集前端传递过来的商品
        cart_data.append(Cart.objects.get(id=goods.id))
        # 保存订单
        order = Order()
        order.order_id = set_order_id(user_id, goods_count, "2")
        # 订单当中有多个商品或者多个店铺，使用goods_count来代替商品id，用2代替店铺id
        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        # 保存订单详情
        # 这里的detail是购物车里的数据实例，不是商品的实例
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order  # order是一条订单数据
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()
            # order是一条订单支付页
        url = "/Buyer/place_order/?order_id=%s" % order.id
        user = Buyer.objects.get(id=int(user_id))
        paid_orders = user.order_set.filter(order_user=user.id, order_status=2)
        for paid_order in paid_orders:
            paid_order_details = paid_order.orderdetail_set.filter(order_id=paid_order.order_id)

    return render(request,"buyer/user_center_order.html",locals())

def user_center_site(request):
    user_id = request.COOKIES.get("user_id")
    address_now = Address.objects.filter(buyer_id=user_id).first()
    if request.method == "POST":
        receiver = request.POST.get("receiver")
        address = request.POST.get("address")
        post_code = request.POST.get("post_code")
        receiver_phone = request.POST.get("receiver_phone")
        addr = Address()
        addr.address = address
        addr.receiver = receiver
        addr.receiver_phone = receiver_phone
        addr.post_code = post_code
        addr.buyer_id = Buyer.objects.get(id=user_id)
        addr.save()
    return render(request,"buyer/user_center_site.html",locals())


def base(request):
    return render(request, "buyer/base.html")





