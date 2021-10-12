from hub_app.models import Hub
from rest_framework import serializers

from geopy.distance import geodesic
import datetime
import random

from order.models import Order
from user_app.models import Address
from user_app.api.serializers import AddressSerializer, UserSerializer


class OrderInitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        exclude = ('payment',)


class OrderListSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

# class OrderListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'






        