from rest_framework_simplejwt.views import TokenObtainPairView
from administrator.api.serializers import AdminTokenObtainPairSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser

from administrator.api.permissions import IsSuperUser


class AdminTokenObtainPairView(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer

