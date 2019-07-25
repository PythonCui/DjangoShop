from django.db import models

class Buyer(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名")
    password = models.CharField(max_length=32, verbose_name="用户密码")
    email = models.EmailField(verbose_name="用户邮箱")
    phone = models.CharField(max_length=32, verbose_name="联系电话")
    connect_address = models.TextField(verbose_name="联系地址")

class Address(models.Model):
    address = models.TextField(verbose_name="联系地址")
    receiver = models.CharField(max_length=32, verbose_name="收件人")
    receiver_phone = models.CharField(max_length=32, verbose_name="收件人电话")
    post_code = models.CharField(max_length=32, verbose_name="邮编")
    buyer_id = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name="买家id")
# Create your models here.

