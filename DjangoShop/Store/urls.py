from django.urls import path, re_path
from Store.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
    re_path('^$', index),
]

urlpatterns += [
    path('base/', base),
]