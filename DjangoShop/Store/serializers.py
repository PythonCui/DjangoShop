from Store.models import Goods
from Store.models import GoodsType

from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Goods
        fields = ['goods_name', 'goods_price', 'goods_number', 'goods_safeDate', 'goods_date', 'id']


class GoodsTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodsType
        fields = ['name','description']