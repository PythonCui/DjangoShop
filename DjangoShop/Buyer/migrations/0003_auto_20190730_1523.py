# Generated by Django 2.1.1 on 2019-07-30 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Buyer', '0002_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='order_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Buyer.Order', verbose_name='订单编号（多对一'),
        ),
    ]