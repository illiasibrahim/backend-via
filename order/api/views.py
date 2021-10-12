from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import razorpay
from rest_framework.decorators import api_view
import requests
from decouple import config

from order.api.serializers import OrderInitSerializer, OrderListSerializer
from order.models import Order, Payment
from order.api import signals
from hub_app.models import Hub
import json
import random
import datetime
from geopy.distance import geodesic
from math import ceil


class CreateOrder(APIView):

    def post(self, request):
        serializer = OrderInitSerializer(data=request.data)
        if serializer.is_valid():
            pickup_location = serializer.validated_data['sender_location']
            pickup = tuple(map(float, pickup_location.split(',')))
            drop_location = serializer.validated_data['receiver_location']
            drop = tuple(map(float, drop_location.split(',')))
            pickup_hub = None
            least_pickup_distance = 15
            drop_hub = None
            least_drop_distance = 15

            hubs = Hub.objects.all()
            for hub in hubs:
                hub_loc = hub.location
                hub_pin = tuple(map(float, hub_loc.split(',')))

                pickup_distance = (geodesic(hub_pin, pickup).km)
                if pickup_distance < least_pickup_distance:
                    least_pickup_distance = pickup_distance
                    pickup_hub = hub

                drop_distance = (geodesic(hub_pin, drop).km)
                if drop_distance < least_drop_distance:
                    least_drop_distance = drop_distance
                    drop_hub = hub

            if drop_hub is not None and pickup_hub is not None:
                data = serializer.save()
                tracking_id = chr(random.randrange(65, 90)) + \
                    datetime.datetime.now().strftime('%S%Y%f%d%H%m%M')
                data.tracking_id = tracking_id
                data.user = request.user
                data.save()
                transit_distance = (
                    geodesic(pickup_location, drop_location).km)
                package_type = serializer.validated_data['type']
                if package_type == 'd':
                    type_coeff = 0.15
                elif package_type == 's':
                    type_coeff = 0.30
                elif package_type == 'm':
                    type_coeff = 0.60
                elif package_type == 'l':
                    type_coeff = 1
                amount = ceil(80 + (transit_distance*0.4*type_coeff))
                rzp_key_1 = config('RZP_KEY_1',cast=str)
                rzp_key_2 = config('RZP_KEY_2',cast=str)
                client = razorpay.Client(auth=(rzp_key_1, rzp_key_2))
                payment = client.order.create({"amount": int(amount) * 100,
                                               "currency": "INR",
                                               "payment_capture": "1"})
                return Response({'success': 'successfully created an order', 'user': data.user.fullname, 'user_email': data.user.email, 'user_phone': data.user.phone, 'payment': payment, 'amount': amount, 'tracking_id': tracking_id})
            elif drop_hub is not None:
                return Response({'error': True, 'drop_service': True, 'pickup_service': False})
            elif pickup_hub is not None:
                return Response({'error': True, 'drop_service': False, 'pickup_service': True})
            else:
                return Response({'error': True, 'drop_service': False, 'pickup_service': False})
        else:
            data = serializer.errors
            return Response(data)


class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user, is_ordered=True).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def handle_payment_success(request):
    res = json.loads(request.data["response"])
    print(res)
    ord_id = ""
    raz_pay_id = ""
    raz_signature = ""

    for key in res.keys():
        if key == 'razorpay_order_id':
            ord_id = res[key]
        elif key == 'razorpay_payment_id':
            raz_pay_id = res[key]
        elif key == 'razorpay_signature':
            raz_signature = res[key]

    data = {
        'razorpay_order_id': ord_id,
        'razorpay_payment_id': raz_pay_id,
        'razorpay_signature': raz_signature
    }

    rzp_key_1 = config('RZP_KEY_1',cast=str)
    rzp_key_2 = config('RZP_KEY_2',cast=str)
    client = razorpay.Client(auth=(rzp_key_1, rzp_key_2))

    check = client.utility.verify_payment_signature(data)

    if check is not None:
        return Response({'error': 'Something went wrong'})

    tracking_id = json.loads(request.data["tracking_id"])
    amount = json.loads(request.data["amount"])

    order = Order.objects.get(tracking_id=tracking_id)

    payment = Payment.objects.create(
        amount_paid=amount, payment_method='razorpay')
    payment.save()

    order.is_ordered = True
    order.payment = payment
    order.save()

    res_data = {
        'message': 'payment successfully received!'
    }

    return Response(res_data)
