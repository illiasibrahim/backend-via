from re import A, search
from user_app.models import Account
from hub_app.models import Hub,Assignment
from order.api.serializers import OrderInitSerializer,OrderListSerializer
from order.models import Order
from user_app.api.serializers import AccountSerializer


from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class HubRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(style={'input_type':'password'},write_only=True)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField()
    phone = serializers.CharField(max_length=15)
    class Meta:
        model = Hub
        fields = ['location','password2','username','password','email','phone']
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2 :
            raise serializers.ValidationError({'error':'Password should be the same'})

        if Account.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error':'Email id already exists'})

        if Account.objects.filter(phone=self.validated_data['phone']):
            raise serializers.ValidationError({'error':'Phone number is already taken'})

        if Account.objects.filter(username=self.validated_data['username']).exists():
            raise serializers.ValidationError({'error':'This username is already been taken'})
        
        account = Account(
            username = self.validated_data['username'],
            email = self.validated_data['email'],
            phone = self.validated_data['phone']
            )
        account.set_password(password)
        account.is_staff = True
        account.save()

        hub = Hub(
            account = account,
            location = self.validated_data['location']
        )
        hub.save()

        return hub

class HubSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    class Meta:
        model = Hub
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        return token

class AssignmentSerializer(serializers.ModelSerializer):
    order = OrderListSerializer(read_only=True)
    class Meta:
        model = Assignment
        exclude = ('hub',)
