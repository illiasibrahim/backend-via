from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
# parsers to get multiple file types from a form
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from decouple import config

from hub_app.api.serializers import HubRegistrationSerializer, CustomTokenObtainPairSerializer, AssignmentSerializer
from hub_app.api.permissions import IsSuperUser, IsStaffUser, IsRequestedStaffUser, IsAuthorizedHub
from hub_app.models import Assignment, Hub
import datetime
import requests
import json
from rider_app.models import Bucket, Task, RiderRequest, Rider
from rider_app.api.serializers import BucketListSerializer, RiderRequestSerializer, TaskListSerializer, RiderSerializer


class HubRegistration(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, format=None):
        serializer = HubRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            hub = serializer.save()
            data = {}
            data['response'] = 'Registration successful'
            data['username'] = hub.account.username
            data['email'] = hub.account.email
            data['phone'] = hub.account.phone

            # refresh = RefreshToken.for_user(hub.account)
            # data['token'] = {
            #     'refresh': str(refresh),
            #     'access':str(refresh.access_token),
            # }

        else:
            data = serializer.errors

        return Response(data)


@api_view(['POST', ])
@permission_classes([IsSuperUser])
def hub_registration_view(request):

    if request.method == 'POST':
        serializer = HubRegistrationSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            hub = serializer.save()

            data['response'] = 'Registration successful'
            data['username'] = hub.account.username
            data['email'] = hub.account.email
            data['phone'] = hub.account.phone

            refresh = RefreshToken.for_user(hub.account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

        else:
            data = serializer.errors

        return Response(data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def create_distance_matrix(hub, now):
    api_key = config('GM_API_KEY')
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_lat}%2C{origin_long}&destinations="
    # the google distance matrix api is in this form
    # url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"
    assignments = Assignment.objects.filter(
        hub=hub, status='initiated', created_at__lt=now).order_by('id')
    count = 1
    for assignment in assignments:
        print(count, assignment.order.sender_landmark)
        count += 1
    # creating a list with all locations that has to be covered by the rider
    locations = [assignment.order.sender_location if assignment.assignment_type ==
                 'collect' else assignment.order.receiver_location for assignment in assignments]

    origin = hub.location
    # inserting the depot (ie. the starting point of the ride) location to the list of points that has to be covered at the first position
    locations.insert(0, origin)
    # google matrix api destinations are bounded to 25 destinations per request
    # so we have to repeat sending requests until every destination is been included in the request
    points_to_cover = len(locations)
    req_dest_limit = 25
    reps = points_to_cover // req_dest_limit
    remainder = points_to_cover % req_dest_limit
    distance_matrix = [[] for y in range(points_to_cover)]
    # this set of nested for loop for including every destination as origin
    for rep in range(0, reps):
        for i in range(rep*req_dest_limit, (rep+1)*req_dest_limit):
            origin = locations[i]
            origin_lat, origin_long = origin.split(',')
            # this set of for loop is to include every location as the destination in the google maps distance matrix api
            for ite in range(0, reps):
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for j in range(ite*req_dest_limit, (ite+1)*req_dest_limit):
                    destination = locations[j]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != (ite+1)*req_dest_limit - 1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

            # to include the remaining locations as destinations which doesn't comes in the repetition loop
            if remainder:
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for rem in range((ite+1)*req_dest_limit, ((ite+1)*req_dest_limit)+remainder):
                    destination = locations[rem]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != ((ite+1)*req_dest_limit)+remainder-1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

    if remainder:
        if reps == 0:
            rep = 0
        else:
            rep += 1

        for i in range(rep*req_dest_limit, rep*req_dest_limit + remainder):
            origin = locations[i]
            origin_lat, origin_long = origin.split(',')
            # this set of for loop is to include every location as the destination in the google maps distance matrix api
            for ite in range(0, reps):
                ind_url = url.format(origin_lat=origin_lat,
                                     origin_long=origin_long)
                for j in range(ite*req_dest_limit, (ite+1)*req_dest_limit):
                    destination = locations[j]
                    destination_lat, destination_long = destination.split(',')
                    ind_url += (destination_lat + "%2C" + destination_long)
                    if j != (ite+1)*req_dest_limit - 1:
                        ind_url += "%7C"
                ind_url += '&key={}'.format(api_key)

                # send a request at this point with an origin and a set of destinations
                response = requests.request(url=ind_url, method='GET')
                res_text = response.text
                res_dict = json.loads(res_text)
                distance_array = []
                for result in res_dict['rows'][0]['elements']:
                    distance = result['distance']['text'][:-3]
                    distance_array.append(
                        (float(distance)*1000) if distance != '' else 0)
                # save the data from the response in the distance matrix
                distance_matrix[i].extend(distance_array)

            # to include the remaining locations as destinations which doesn't comes in the repetition loop
            ind_url = url.format(origin_lat=origin_lat,
                                 origin_long=origin_long)
            if reps == 0:
                ite = 0
            else:
                ite += 1
            for rem in range((ite)*req_dest_limit, ((ite)*req_dest_limit)+remainder):
                destination = locations[rem]
                destination_lat, destination_long = destination.split(',')
                ind_url += (destination_lat + "%2C" + destination_long)
                if rem != ((ite)*req_dest_limit)+remainder-1:
                    ind_url += "%7C"
            ind_url += '&key={}'.format(api_key)

            # send a request at this point with an origin and a set of destinations
            response = requests.request(url=ind_url, method='GET')
            res_text = response.text
            res_dict = json.loads(res_text)
            distance_array = []
            for result in res_dict['rows'][0]['elements']:
                distance = result['distance']['text'][:-3]
                distance_array.append(
                    (float(distance)*1000) if distance != '' else 0)
            # save the data from the response in the distance matrix
            distance_matrix[i].extend(distance_array)

    return distance_matrix


def create_data_model(hub, now):
    """Stores the data for the problem."""
    data = {}
    distance_matrix = create_distance_matrix(hub, now)

    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = 3
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""

    # print(f'Objective: {solution.ObjectiveValue()}')
    # max_route_distance = 0
    routes = {}
    for vehicle_id in range(data['num_vehicles']):
        routes[vehicle_id] = {'path': []}
        index = routing.Start(vehicle_id)
        # plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        index = solution.Value(routing.NextVar(index))
        while not routing.IsEnd(index):
            routes[vehicle_id]['path'].extend([index])
            # plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        # plan_output += '{}\n'.format(manager.IndexToNode(index))
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        routes[vehicle_id]['distance'] = route_distance
        # print(plan_output)
        # max_route_distance = max(route_distance, max_route_distance)
    # print('Maximum of the route distances: {}m'.format(max_route_distance))
    print(routes)
    return routes


def main(hub, now):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(hub, now)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        300000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    # Print solution on console.
    if solution:
        routes = print_solution(data, manager, routing, solution)
    else:
        routes = None
    return routes


def populate_buckets(hub, now, optimized_routes):
    assignments = Assignment.objects.filter(
        hub=hub, status='initiated', created_at__lt=now).order_by('id')
    for assignment in assignments:
        print(assignment)
    for route in optimized_routes.keys():
        bucket = Bucket(hub=hub, distance=optimized_routes[route]['distance'])
        bucket.save()
        for destination in optimized_routes[route]['path']:
            print('index :  ', destination-1)
            assignment = assignments[destination-1]
            assignment.status = 'assigned'
            assignment.save()
            task = Task(bucket=bucket, assignment=assignment)
            task.save()
    return


class AssignmentList(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        for assignment in Assignment.objects.all():
            assignment.status = 'initiated'
            assignment.save()
        return Assignment.objects.filter(hub__account=self.request.user, status='initiated')


class PopulateBucketView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, format=None):
        hub = Hub.objects.get(account=self.request.user)
        now = datetime.datetime.now()
        # solving the problem with google OR Tools
        optimized_routes = main(hub, now)
        populate_buckets(hub, now, optimized_routes)
        buckets = Bucket.objects.filter(hub=hub)
        serializer = BucketListSerializer(buckets, many=True)
        print('completed in : ', datetime.datetime.now() - now)
        return Response(serializer.data)


class BucketListView(generics.ListAPIView):
    serializer_class = BucketListSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return Bucket.objects.filter(hub__account=self.request.user)


class RiderRequestListView(generics.ListAPIView):
    serializer_class = RiderRequestSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return RiderRequest.objects.filter(hub__account=self.request.user)

class RiderRequestAcceptView(APIView):
    permission_classes = [IsRequestedStaffUser]

    def get(self, request,id, format=None):
        rider_request = RiderRequest.objects.get(id = id)
        if rider_request.active:
            self.check_object_permissions(request,rider_request)
            hub = Hub.objects.get(account = request.user)
            rider = rider_request.rider
            rider.hub = hub
            rider.save()
            rider_request.active = False
            rider_request.save()
            rider_requests = RiderRequest.objects.filter(hub__account=self.request.user)
            serializer = RiderRequestSerializer(rider_requests,many=True)
            return Response({'success':True, 'message':'Added rider to the hub','data':serializer.data})
        return Response({'success':False, 'message':'Inactive request'})

class RiderRequestRejectView(APIView):
    permission_classes = [IsRequestedStaffUser]

    def get(self, request, id, format=None):
        rider_request = RiderRequest.objects.get(id=id)
        if rider_request.active:
            self.check_object_permissions(request,rider_request)
            rider_request.active = False
            rider_request.save()
            rider_requests = RiderRequest.objects.filter(hub__account = self.request.user)
            serializer = RiderRequestSerializer(rider_requests, many=True)
            return Response({'success':True, "message":"Rejected the rider request", 'data':serializer.data})
        return Response({'success':False, 'message':"Inactive request"})

class RiderListView(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = RiderSerializer

    def get_queryset(self):
        hub = Hub.objects.get(account= self.request.user)
        return Rider.objects.filter(hub=hub)

class RiderRelieveView(APIView):
    permission_classes = [IsAuthorizedHub]

    def get(self, request, id, format=None):
        rider = Rider.objects.get(id=id)
        self.check_object_permissions(request,rider)
        rider.hub = None
        rider.save()
        riders = Rider.objects.filter(hub__account=request.user)
        serializer = RiderSerializer(riders,many=True)
        return Response(serializer.data)