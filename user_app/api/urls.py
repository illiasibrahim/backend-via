from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from user_app.api import views

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/',views.user_registration_view, name='user-register'),
    path('address/',views.AddressList.as_view(),name='user-address-list'),
    path('address/<int:pk>/',views.AddressDetail.as_view(),name='user-address-detail'),
    path('check/',views.check_availability,name='check-availability'),
    path('quote/',views.get_quote,name='get-quote'),
    path('profile/',views.ViewProfile.as_view(),name='show-profile'),
]