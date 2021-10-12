from user_app.models import Account,Address

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)

    class Meta:
        model = Account
        fields = ['fullname',  'email', 'username', 'phone', 'password', 'password2']
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
        
        account = Account(
            fullname=self.validated_data['fullname'],
            username = self.validated_data['username'],
            email = self.validated_data['email'],
            phone = self.validated_data['phone']
            )
        account.set_password(password)
        account.save()

        return account

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email','phone','username')

