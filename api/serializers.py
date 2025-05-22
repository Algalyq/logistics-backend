from rest_framework import serializers
from .models import CustomUser
from .models import (
    Location, Order, DeliveryTracking, UserProfile,
    DriverDocument, Truck, Analytics
)
from rest_framework.validators import UniqueValidator
from django.core.validators import MinValueValidator, MaxValueValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        read_only_fields = ['id']

class DriverDocumentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    document_type_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DriverDocument
        fields = ['id', 'document_type', 'document_type_display', 'document_number', 'issue_date', 'expiry_date', 'image', 'image_url']
        read_only_fields = ['id', 'image_url', 'document_type_display']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_document_type_display(self, obj):
        return obj.get_document_type_display()

class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = [
            'id', 'license_plate', 'model', 'year', 'truck_type',
            'max_weight', 'length', 'tachograph_expiry', 'is_active'
        ]
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    documents = DriverDocumentSerializer(many=True, read_only=True)
    assigned_truck = TruckSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'phone', 'role', 'experience_years', 
            'total_kilometers', 'documents', 'assigned_truck'
        ]
        read_only_fields = ['role']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'experience_years', 'total_kilometers']
        read_only_fields = ['user', 'role']



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
    distance = serializers.FloatField(read_only=True)  # in kilometers
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer_name', 'origin_name', 'destination_name',
            'vehicle_type', 'product_type', 'weight', 'price', 'status', 'date',
            'driver_name', 'estimated_arrival', 'delivered_on', 'reason', 'distance'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True, allow_null=True)
    date = serializers.DateTimeField(source='created_at', format="%Y-%m-%d", read_only=True)
    distance = serializers.FloatField(read_only=True)  # in kilometers
    truck_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer', 'origin', 'destination',
            'vehicle_type', 'product_type', 'weight', 'price', 'status', 'date',
            'driver', 'estimated_arrival', 'delivered_on', 'reason',
            'distance', 'truck_details'
        ]
    
    def get_truck_details(self, obj):
        if hasattr(obj, 'truck') and obj.truck:
            return TruckSerializer(obj.truck).data
        return None

class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'origin', 'destination', 'vehicle_type', 'product_type',
            'weight', 'price', 'estimated_arrival'
        ]
        extra_kwargs = {
            'origin': {'required': True},
            'destination': {'required': True},
            'vehicle_type': {'required': True},
            'product_type': {'required': True},
            'weight': {'required': True},
            'price': {'required': True},
        }

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

class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = [
            'month_year', 'total_orders', 'completed_orders',
            'total_distance', 'total_revenue', 'average_rating'
        ]
        read_only_fields = fields

class DriverDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocument
        fields = ['document_type', 'document_number', 'issue_date', 'expiry_date', 'image']
        extra_kwargs = {
            'document_type': {'required': True},
            'document_number': {'required': True},
            'issue_date': {'required': True},
            'expiry_date': {'required': True},
        }

class DriverRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)
    experience_years = serializers.IntegerField(required=False, default=0)
    
    def generate_credentials(self):
        # Generate a random username based on first name and last name
        import random
        import string
        
        first_name = self.validated_data['first_name'].lower()
        last_name = self.validated_data['last_name'].lower()
        base_username = f"{first_name[0]}{last_name}"[:15]  # First letter of first name + last name, max 15 chars
        
        # Check if username exists, if yes, add a random number
        username = base_username
        while CustomUser.objects.filter(username=username).exists():
            random_suffix = ''.join(random.choices(string.digits, k=3))
            username = f"{base_username}{random_suffix}"[:15]
            
        # Generate a random password (8 characters)
        password = ''.join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, 
            k=8
        ))
        
        return username, password
    
    def create(self, validated_data):
        username, password = self.generate_credentials()
        
        # Create the user with role='driver'
        user = CustomUser.objects.create(
            username=username,
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='driver',
            phone=validated_data.get('phone', '')
        )
        user.set_password(password)
        user.save()
        
        # Create user profile for driver-specific fields
        UserProfile.objects.create(
            user=user,
            role='driver',  # Keep this for backward compatibility
            phone=validated_data.get('phone', ''),
            experience_years=validated_data.get('experience_years', 0)
        )
        
        # Return user and generated credentials
        return {
            'user': user,
            'username': username,
            'password': password
        }


class DriverProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    documents = DriverDocumentSerializer(many=True, read_only=True)
    assigned_truck = TruckSerializer(read_only=True)
    analytics = AnalyticsSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'user', 'phone', 'experience_years', 'total_kilometers',
            'documents', 'assigned_truck', 'analytics'
        ]