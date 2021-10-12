from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers



class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_admin'] = user.is_super_admin
        return token
