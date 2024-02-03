from rest_framework import serializers
from django.contrib.auth.models import User
# from .models import Location

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


# class LocationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Location
#         fields = ['location_id', 'longitude', 'latitude', 'user']
