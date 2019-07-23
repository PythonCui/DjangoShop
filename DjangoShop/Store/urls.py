from django.urls import path, re_path
from Store.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
    path('register_store/', register_store),
    path('add_goods/', add_goods),
    path('list_goods/', list_goods),
    re_path('^$', index),
]

urlpatterns += [
    path('base/', base),
]