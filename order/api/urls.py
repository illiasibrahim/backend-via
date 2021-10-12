from django.urls import path

from order.api import views

urlpatterns = [
    path('create/',views.CreateOrder.as_view(),name='create-order'),
    path('list/',views.OrderList.as_view(),name='order-list'),
    path('razorpay/success/',views.handle_payment_success,name='razorpay-success')
]