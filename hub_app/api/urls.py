from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from hub_app.api import views

urlpatterns = [
    path('api/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/',views.HubRegistration.as_view(),name='hub-register'),
    path('assignment/list/',views.AssignmentList.as_view(),name='assignment-list'),
    path('bucket/populate/',views.PopulateBucketView.as_view(),name='populate-bucket'),
    path('bucket/list/',views.BucketListView.as_view(),name='bucket-list'),
    path('request/list/',views.RiderRequestListView.as_view(),name='request-list'),
    path('request/<id>/accept/',views.RiderRequestAcceptView.as_view(),name='request-accept'),
    path('request/<id>/reject/',views.RiderRequestRejectView.as_view(),name='request-reject'),
    path('rider/list/',views.RiderListView.as_view(),name='rider-list'),
    path('rider/<id>/relieve/',views.RiderRelieveView.as_view(),name='rider-relieve'),
]
