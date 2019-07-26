from django.urls import path, re_path
from Buyer.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('index/', index),
    path('pay_order/', pay_order),
    path('pay_result/', pay_result),
    path('goods_list/', goods_list),
]

urlpatterns += [
    path('base/',base),
]
