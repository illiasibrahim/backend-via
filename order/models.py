from django.db import models

from user_app.models import Account,Address

class Payment(models.Model):
    amount_paid = models.IntegerField()
    payment_method = models.CharField(max_length=20)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.payment_method + str(self.amount_paid))

class Order(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='orders',null=True)
    type = models.CharField(max_length=30)
    category = models.CharField(max_length=40,default=None,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=70,default='Order placed')
    payment = models.OneToOneField(Payment,on_delete=models.CASCADE,related_name='pay',null=True)
    tracking_id = models.CharField(max_length=30,default=0)
    sender_name = models.CharField(max_length=30)
    sender_building = models.CharField(max_length=30)
    sender_city = models.CharField(max_length=30)
    sender_pin = models.CharField(max_length=10)
    sender_phone = models.CharField(max_length=15)
    sender_location = models.CharField(max_length=30)
    sender_landmark = models.CharField(max_length=128)
    receiver_name = models.CharField(max_length=30)
    receiver_building = models.CharField(max_length=30)
    receiver_city = models.CharField(max_length=30)
    receiver_pin = models.CharField(max_length=10)
    receiver_phone = models.CharField(max_length=15)
    receiver_location = models.CharField(max_length=30)
    receiver_landmark = models.CharField(max_length=128)
    is_ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.tracking_id)
