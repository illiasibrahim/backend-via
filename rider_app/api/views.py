from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from rest_framework import status

from django.core import exceptions
from geopy.distance import geodesic

from rider_app.api.serializers import RiderRegistrationSerializer, RiderTokenObtainPairSerializer, TaskListSerializer, BucketListSerializer, RiderSerializer, RiderRequestSerializer
from rider_app.models import Bucket, Task, Rider, RiderRequest
from rider_app.api.permissions import IsRider, IsAssignedRider, IsHubRider, IsInactiveRider, IsActiveRider
from rider_app.actions import string_to_tuple
from hub_app.models import Hub
from hub_app.api.serializers import HubSerializer


class RiderRegistration(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = RiderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            rider = serializer.save()
            data = {}
            data['response'] = 'Registration successful'
            data['is_rider'] = rider.account.is_rider
            refresh = RefreshToken.for_user(rider.account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            data = serializer.errors
        return Response(data)


class RiderTokenObtainPairView(TokenObtainPairView):
    serializer_class = RiderTokenObtainPairSerializer


class AcceptBucketView(APIView):

    permission_classes = [IsHubRider]

    def get(self, request, id, format=None):
        bucket = Bucket.objects.get(id=id)
        # assign rider to bucket
        rider = Rider.objects.get(account=request.user)
        bucket.rider = rider
        bucket.save()
        self.check_object_permissions(request, bucket)
        # assign a rider to this bucket
        tasks = Task.objects.filter(bucket=bucket).order_by('id')
        for task in tasks:
            print('task : ', task.assignment.order)
            # assign rider to this task
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


class DeliverySuccess(APIView):

    permission_classes = [IsAssignedRider]

    def get(self, request, id, format=None):
        try:
            task = Task.objects.get(id=id)
            self.check_object_permissions(request, task)
            task.status = 'completed'
            task.save()
            success = True
        except:
            success = False
        return Response({'success': success})


class DeliveryRetry(APIView):

    permission_classes = [IsAssignedRider]

    def get(self, request, id, format=None):
        try:
            task = Task.objects.get(id=id)
            self.check_object_permissions(request, task)
            task.status = 'tried'
            task.save()
            response = {"success": True}
        except Task.DoesNotExist:
            response = {"success": False, "message": "Task does not exist"}
        except:
            response = {
                "success": False, "message": "You don't have permission to do this operation"}
        return Response(response)


class TaskListView(APIView):

    permission_classes = [IsAssignedRider]

    def get(self, request, id, format=None):
        try:
            bucket = Bucket.objects.get(id=id)
            self.check_object_permissions(request, bucket)
        except Bucket.DoesNotExist:
            return Response({'message': 'Object does not exist'}, status=status.HTTP_404_NOT_FOUND)
        tasks = Task.objects.filter(bucket__id=id)
        serailizer = TaskListSerializer(tasks, many=True)
        return Response(serailizer.data)


class BucketListView(generics.ListAPIView):
    serializer_class = BucketListSerializer
    permission_classes = [IsActiveRider]

    def get_queryset(self):
        return Bucket.objects.filter(rider__account=self.request.user)


class RiderProfileView(APIView):
    permission_classes = [IsRider]

    def get(self, request, format=None):
        rider = Rider.objects.get(account=request.user)
        serializer = RiderSerializer(rider)
        return Response(serializer.data)


class FindHubView(APIView):
    permission_classes = [IsRider]

    def get(self, request, format=None):
        location = request.query_params.get('location')
        if not location:
            return Response({'success': False, 'message': 'Please include location in the query parameter'})
        hubs = Hub.objects.all()
        nearest_hub = None
        minimum_distance = 15
        for hub in hubs:
            hub_location = string_to_tuple(hub.location)
            distance = geodesic(string_to_tuple(location), hub_location)
            if distance < minimum_distance:
                minimum_distance = distance
                nearest_hub = hub

        if nearest_hub is not None:
            serailizer = HubSerializer(nearest_hub)
            return Response({'found': True, 'data': serailizer.data})
        return Response({'found': False})


class RiderRequestView(APIView):
    permission_classes = [IsInactiveRider]
    def get(self, request, format=None):
        hub_id = request.query_params.get('hub')
        try:
            hub = Hub.objects.get(id=hub_id)
        except:
            return Response({'success': False, 'message': 'Invalid Hub id'}, status=status.HTTP_404_NOT_FOUND)
        location = request.query_params.get('location')
        try:
            rider = Rider.objects.get(account=request.user)
        except:
            return Response({'success': False, 'message': 'Make sure you are logged in'}, status=status.HTTP_404_NOT_FOUND)

        distance = geodesic(string_to_tuple(location),
                            string_to_tuple(hub.location))
        if distance < 15:
            if RiderRequest.objects.filter(hub=hub, rider=rider, active=True).exists():
                return Response({'success': 'False', 'message': 'active request exists'})
            else:
                rider_request = RiderRequest(
                    hub=hub, location=location, rider=rider)
                rider_request.save()
                serializer = RiderRequestSerializer(rider_request)
                return Response({'success': True, 'message': 'successfully created request', 'data': serializer.data})

        return Response({'success': False, 'message': 'location outside delivery circle '})

class RiderRequestListView(APIView):
    permission_classes = [IsRider]

    def get(self, request, format=None):
        requests = RiderRequest.objects.filter(rider__account = request.user)
        serializer = RiderRequestSerializer(requests, many=True)
        return Response(serializer.data)