from django.db import models

from django.utils.translation import ugettext_lazy as _

from user_app.models import Account
from order.models import Order

def upload_to(instance, filename):
    return 'posts/{filename}'.format(filename=filename) 


class Hub(models.Model):
    location = models.CharField(max_length=80)
    account = models.OneToOneField(Account,on_delete=models.CASCADE,related_name='hub')


    def __str__(self):
        return self.account.username

# class Image(models.Model):
#     photo = models.ImageField(_('Image'), upload_to=upload_to, blank=True)

class Assignment(models.Model):

    type_choices = {
        ('forward','forward'),
        ('return','return'),
    }

    status_choices = {
        ('initiated','initiated'),
        ('assigned','assigned'),
        ('collected','collected'),
        ('delivered','delivered'),
        ('cancelled','cancelled')
    }


    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order')
    hub = models.ForeignKey(Hub,on_delete=models.CASCADE,related_name='hub')
    try_count = models.IntegerField(default=0)
    transit_type = models.CharField(max_length=40,choices=type_choices,default='forward')
    status = models.CharField(max_length=200, choices=status_choices,default='initiated')
    container = models.CharField(max_length=30,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assignment_type = models.CharField(max_length=128, default='collect')

    def __str__(self):
        return self.order.tracking_id + "-" + self.transit_type

