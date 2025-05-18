from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Location, Order, DeliveryTracking, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone', 'role']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude']

class OrderListSerializer(serializers.ModelSerializer):
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True, allow_null=True)
    date = serializers.DateTimeField(source='created_at', format="%Y-%m-%d", read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer_name', 'origin_name', 'destination_name',
            'vehicle_type', 'product_type', 'weight', 'price', 'status', 'date',
            'driver_name', 'estimated_arrival', 'delivered_on', 'reason'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True, allow_null=True)
    date = serializers.DateTimeField(source='created_at', format="%Y-%m-%d", read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'origin', 'destination',
            'vehicle_type', 'product_type', 'weight', 'price', 'status', 'date',
            'driver', 'estimated_arrival', 'delivered_on', 'reason'
        ]

class DeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = ['id', 'order', 'latitude', 'longitude', 'timestamp', 'progress']
        read_only_fields = ['id', 'timestamp']

class LatestTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = ['latitude', 'longitude', 'timestamp', 'progress']
        read_only_fields = ['timestamp']
