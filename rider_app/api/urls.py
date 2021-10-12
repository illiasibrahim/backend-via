from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from rider_app.api import views

urlpatterns = [
    path('login/', views.RiderTokenObtainPairView.as_view(), name='rider_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='rider_token_refresh'),
    path('register/',views.RiderRegistration.as_view(),name='rider_register'),
    # path('upload/',views.UploadImage.as_view(), name='upload-image'),
    path('bucket/<id>/accept/', views.AcceptBucketView.as_view(), name='accept-bucket'),
    path('task/<id>/success/',views.DeliverySuccess.as_view(),name='delivery-success'),
    path('task/<id>/retry/',views.DeliveryRetry.as_view(),name='delivery-retry'),
    path('bucket/<id>/tasks/',views.TaskListView.as_view(),name='bucket-task-list'),
    path('bucket/list/',views.BucketListView.as_view(),name='list-buckets'),
    path('profile/',views.RiderProfileView.as_view(),name='profile'),
    path('find/hub/',views.FindHubView.as_view(),name='find-hub'),
    path('request/hub/',views.RiderRequestView.as_view(),name='request-hub'),
    path('request/list/',views.RiderRequestListView.as_view(),name='rider-request-list'),
]
