from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Location, Order, DeliveryTracking, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, LocationSerializer,
    OrderListSerializer, OrderDetailSerializer, DeliveryTrackingSerializer,
    LatestTrackingSerializer
)

# User registration and authentication views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user, role='customer')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Locations API (Kazakhstan cities)
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]  # Public access to city list

# Orders API
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        
        # Filter queryset based on user role
        if profile.role == 'admin':
            # Admins see all orders
            return Order.objects.all().order_by('-created_at')
        elif profile.role == 'driver':
            # Drivers see orders assigned to them
            return Order.objects.filter(driver=user).order_by('-created_at')
        else:
            # Customers see their own orders
            return Order.objects.filter(customer=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

# API for new orders available for drivers
class NewOrdersView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(status='new').order_by('-created_at')

# Driver's orders API
class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        
        if profile.role == 'driver':
            return Order.objects.filter(driver=user).exclude(status='new').order_by('-created_at')
        return Order.objects.filter(customer=user).exclude(status='new').order_by('-created_at')

# Delivery tracking API
class DeliveryTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryTrackingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DeliveryTracking.objects.all()

# Get latest tracking info for an order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_tracking(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    tracking = DeliveryTracking.objects.filter(order=order).order_by('-timestamp').first()
    
    if not tracking:
        # If no tracking data exists, create a default one at 0% progress
        tracking = DeliveryTracking.objects.create(
            order=order,
            latitude=order.origin.latitude,
            longitude=order.origin.longitude,
            progress=0
        )
    
    serializer = LatestTrackingSerializer(tracking)
    return Response(serializer.data)

# Update order status
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    new_status = request.data.get('status')
    
    if new_status and new_status in [status for status, _ in Order.STATUS_CHOICES]:
        order.status = new_status
        order.save()
        return Response({"status": "success", "message": f"Order status updated to {new_status}"})
    
    return Response({"status": "error", "message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
