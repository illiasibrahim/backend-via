from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from administrator.api import views

urlpatterns = [
    path('login/', views.AdminTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]