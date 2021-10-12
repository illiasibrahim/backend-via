from django.db import models
from django.utils.translation import ugettext_lazy as _
import os

from user_app.models import Account
from hub_app.models import Hub, Assignment

# Create your models here.


def get_upload_path(instance, filename):
    return os.path.join(
        "user_%s" % instance.account.username, filename)


class Rider(models.Model):
    account = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name='account')
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL,
                            null=True, related_name='delivery_boy')
    id_proof = models.ImageField(
        _('id_proof'), upload_to=get_upload_path, null=True)
    photo = models.ImageField(upload_to=get_upload_path, null=True)

    def __str__(self):
        return self.account.username


class Bucket(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True)
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    distance = models.CharField(max_length=10)

    def __str__(self):
        return self.hub.account.username + str(self.id)


class Task(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'initiated'),
        ('assigned', 'assigned'),
        ('completed', 'completed'),
        ('tried', 'tried'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=32, choices=STATUS_CHOICES, default='initiated')
    bucket = models.ForeignKey(
        Bucket, on_delete=models.SET_NULL, null=True, related_name='tasks')

    def __str__(self):
        return (self.assignment.order.tracking_id + str(self.id))


class RiderRequest(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    location = models.CharField(max_length=64)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.location + self.rider.account.username
