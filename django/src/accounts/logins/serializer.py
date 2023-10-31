from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'user_name', 'email', 'password')
        extra_kwargs = {
            'user_name': {'required':False,'validators':[],},
            'email': {'required':False,'validators':[],},
            'password': {'write_only': True, 'required':False},
        }

    def create(self, user_name, email, password):
        return User.objects.create_user(user_name=user_name, 
                                        email=email, 
                                        password=password)
    
    def update(self, user, fields):
        return User.objects.update_user(user, fields)

    def is_valid(self, valid_fields=(), raise_exception=False, *args):
        if valid_fields:
            self.initial_data = {k:v for k,v in self.initial_data.items() if(k in valid_fields)}
        return super().is_valid(*args,raise_exception=False)