from django.urls import path, re_path
from Buyer.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('index/', index),
    path('cart/', cart),
    path('add_cart/', add_cart),
    path('user_center_info/', user_center_info),
    path('user_center_order/', user_center_order),
    path('user_center_site/', user_center_site),
    path('pay_order/', pay_order),
    path('pay_result/', pay_result),
    path('goods_list/', goods_list),
    path('detail/', detail),
    path('place_order/', place_order),
]

urlpatterns += [
    path('base/',base),
]
