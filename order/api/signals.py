from django.db.models.signals import post_save

from order.models import Order
from hub_app.models import Assignment, Hub

from geopy.distance import geodesic
import datetime


def order_create_handler(sender, instance, created, *args, **kwargs):
    print(instance)
    nearest_hub = None
    least_distance = 20
    if created:
        origin_loc = instance.sender_location

        origin = tuple(map(float,origin_loc.split(',')))
        hubs = Hub.objects.all()
        for hub in hubs:
            dest_loc = hub.location
            destination = tuple(map(float,dest_loc.split(',')))

            if (geodesic(origin, destination).km) < least_distance:
                nearest_hub = hub
        
        
        if nearest_hub:
            assignment = Assignment(
                order = instance,
                hub = nearest_hub
            )
            assignment.save()



post_save.connect(order_create_handler, sender=Order)