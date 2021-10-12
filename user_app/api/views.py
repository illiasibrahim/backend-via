from rest_framework.response import Response 
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
import requests
import json
import ast
from geopy.distance import geodesic
from rest_framework.views import APIView

from hub_app.models import Hub
from user_app.models import Account, Address
from user_app.api.permissions import IsAddressAuthor
from user_app.api.serializers import AddressSerializer, UserRegistrationSerializer,AccountSerializer



@api_view(['POST',])
def user_registration_view(request):

    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            account = serializer.save()

            data['response'] = 'Registration successful'
            data['username'] = account.username
            data['email'] = account.email
            data['fullname'] = account.fullname
            data['phone'] = account.phone
            
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access':str(refresh.access_token),
            }

        else:
            data = serializer.errors
        
        
        return Response(data)


class AddressList(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self,serializer):
        user = self.request.user
        serializer.save(user=user)

class AddressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAddressAuthor]

@api_view(['GET'])
def check_availability(request):
    pickup_pin=request.query_params.get('pickup_pin')
    drop_pin=request.query_params.get('drop_pin')

    url = "https://vialocations.herokuapp.com/pin/lookup/?pin={pin}".format(pin=pickup_pin)
    pickup_response = requests.request("GET", url)
    pickup_content = (pickup_response.json())
    pickup_coordinate = None
    if (pickup_content['data']):
        pickup_coordinate = (pickup_content['data'][0]['coordinates'])
    url = "https://vialocations.herokuapp.com/pin/lookup/?pin={pin}".format(pin=drop_pin)
    drop_response = requests.request("GET", url)
    drop_content = (drop_response.json())
    drop_coordinate = None
    if (drop_content['data']):
        drop_coordinate = (drop_content['data'][0]['coordinates'])
    
    if not drop_coordinate or not pickup_coordinate:
        return Response({'found':False})
    hubs = Hub.objects.all()
    least_pickup_distance = 15
    pickup_hub = None
    least_drop_distance = 15
    drop_hub = None
    for hub in hubs:
        hub_loc = hub.location
        hub_coordinate = tuple(map(float,hub_loc.split(',')))

        pickup_distance = (geodesic(hub_coordinate,pickup_coordinate).km)
        if pickup_distance < least_pickup_distance:
            least_pickup_distance = pickup_distance
            pickup_hub = hub
        
        drop_distance = (geodesic(hub_coordinate,drop_coordinate).km)
        if drop_distance < least_drop_distance:
            least_drop_distance = drop_distance
            drop_hub = hub
    
    if drop_hub is None and pickup_hub is None:
        return Response({'found':True,'pickup_service':False,'drop_service':False})
    elif drop_hub is None:
        return Response({'found':True,'pickup_service':True,'drop_service':False})
    elif pickup_hub is None:
        return Response({'found':True,'pickup_service':False,'drop_service':True})
    else:
        return Response({'found':True,'pickup_service':True,'drop_service':True})


@api_view(['GET'])   
def get_quote(request):
    pickup_pin=request.query_params.get('pickup_pin')
    drop_pin=request.query_params.get('drop_pin')
    package_type= request.query_params.get('package_type')  

    url = "https://vialocations.herokuapp.com/pin/lookup/?pin={pin}".format(pin=pickup_pin)
    pickup_response = requests.request("GET", url)
    pickup_content = (pickup_response.json())
    pickup_coordinate = None
    if (pickup_content['data']):
        pickup_coordinate = (pickup_content['data'][0]['coordinates'])
    url = "https://vialocations.herokuapp.com/pin/lookup/?pin={pin}".format(pin=drop_pin)
    drop_response = requests.request("GET", url)
    drop_content = (drop_response.json())
    drop_coordinate = None
    if (drop_content['data']):
        drop_coordinate = (drop_content['data'][0]['coordinates'])
    
    if drop_coordinate is None and pickup_coordinate is None:
        return Response({'pickup_found':False,'drop_found':False})
    
    elif drop_coordinate is None:
        return Response({'pickup_found':True, 'Drop_found':False})

    elif pickup_coordinate is None:
        return Response({'pickup_found':False, 'drop_found':True})

    pickup_hub = None
    least_pickup_distance = 15
    drop_hub = None
    least_drop_distance = 15

    hubs = Hub.objects.all()
    for hub in hubs:
        hub_loc = hub.location
        hub_coordinate = tuple(map(float,hub_loc.split(',')))
        
        pickup_distance = (geodesic(hub_coordinate,pickup_coordinate).km)
        if pickup_distance < least_pickup_distance:
            least_pickup_distance = pickup_distance
            pickup_hub = hub 

        drop_distance = (geodesic(hub_coordinate,drop_coordinate).km)
        if drop_distance < least_drop_distance:
            least_drop_distance = drop_distance
            drop_hub = hub
        
    if drop_hub is not None and pickup_hub is not None:
        transit_distance = (geodesic(pickup_coordinate,drop_coordinate).km)
        if package_type == 'd':
            type_coeff = 0.15
        elif package_type == 's':
            type_coeff = 0.30
        elif package_type == 'm':
            type_coeff = 0.60
        elif package_type == 'l':
            type_coeff = 1
        amount = int(80 + (transit_distance*0.4*type_coeff))
        return Response({'pickup_found':True,'drop_found':True,'pickup_service':True,'drop_service':True, 'amount':amount})
    
    elif drop_hub is not None:
        return Response({'pickup_found':True,'drop_found':True,'pickup_service':False,'drop_service':True})
    
    elif pickup_hub is not None:
        return Response({'pickup_found':True,'drop_found':True,'pickup_service':True,'drop_service':False})
    
    else:
        return Response({'pickup_found':True,'drop_found':True,'pickup_service':False,'drop_service':False})


class ViewProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        serializer = AccountSerializer(user)
        return Response(serializer.data)