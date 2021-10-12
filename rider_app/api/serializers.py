from user_app.models import Account
from rider_app.models import Bucket, Rider, Task, RiderRequest
from hub_app.api.serializers import AssignmentSerializer, HubSerializer
from user_app.api.serializers import UserSerializer

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RiderRegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=30)
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(style={'input_type': 'password'},write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'},write_only=True)
    id_proof = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    photo = serializers.ImageField(max_length=None,use_url=True, allow_null=True, required=False)

    class Meta:
        model = Rider
        fields = ['fullname', 'username', 'email', 'phone', 'password', 'password2','id_proof','photo']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'error':'Password should be the same'})

        if Account.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error':'Email id already exists'})
        
        if Account.objects.filter(phone=self.validated_data['phone']).exists():
            raise serializers.ValidationError({'error':'This phone number is already been used'})

        if Account.objects.filter(username=self.validated_data['username']):
            raise serializers.ValidationError({'error':'This username is already been taken'})

        account = Account(
            fullname = self.validated_data['fullname'],
            username = self.validated_data['username'],
            phone = self.validated_data['phone'],
            email = self.validated_data['email']
        )
        
        account.set_password(password)
        account.is_rider = True
        account.save()
        
        rider = Rider(
            account = account,
            id_proof = self.validated_data['id_proof'],
            photo = self.validated_data['photo']
        )
        rider.save()

        return rider

class RiderSerializer(serializers.ModelSerializer):
    account = UserSerializer()
    class Meta:
        model = Rider
        fields = '__all__'

class RiderTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_rider'] = user.is_rider
        return token

class TaskListSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    class Meta:
        model = Task
        fields = '__all__'

class BucketListSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(read_only=True,many=True)
    class Meta:
        model = Bucket
        fields = '__all__'

class RiderRequestSerializer(serializers.ModelSerializer):
    rider = RiderSerializer(read_only=True)
    hub = HubSerializer(read_only=True)
    class Meta:
        model = RiderRequest
        fields = '__all__'

