import datetime
from rest_framework import viewsets, permissions, status, generics, mixins, views
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import (
    Location, Order, DeliveryTracking, UserProfile,
    DriverDocument, Truck, Analytics
)
from .serializers import *

# User registration and authentication views
class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Set the role as 'customer' for new registrations
            user = serializer.save(role='customer')
            user.set_password(request.data.get('password'))
            user.save()
            
            # Create user profile for backward compatibility
            UserProfile.objects.create(
                user=user, 
                role='customer',
                phone=user.phone
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the user's auth token to logout
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class DriverRegistrationView(generics.CreateAPIView):
    serializer_class = DriverRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Only customers can create drivers
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'customer':
            return Response(
                {"detail": "Only customers can register drivers"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            
            # Return data including generated credentials and role
            response_data = {
                'id': result['user'].id,
                'username': result['username'],
                'password': result['password'],  # This will be shown only once
                'email': result['user'].email,
                'first_name': result['user'].first_name,
                'last_name': result['user'].last_name,
                'role': 'driver',
                'phone': result['user'].profile.phone
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Profile Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user.profile
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

# Driver Profile Views
class DriverProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverProfileSerializer
    
    def get_queryset(self):
        return UserProfile.objects.filter(role='driver')
    
    def get_object(self):
        return self.request.user.profile

class DriverDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverDocumentSerializer
    
    def get_serializer_context(self):
        # Include request in context for generating image URLs
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        # Get documents directly related to the user
        return DriverDocument.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Create the document and directly associate it with the user
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['get'])
    def view_document(self, request, pk=None):
        """View a specific document with formatted details"""
        document = self.get_object()
        serializer = self.get_serializer(document)
        
        # Format response with localized information
        data = serializer.data
        
        # Add additional formatted information
        data['issue_date_formatted'] = document.issue_date.strftime('%d %B %Y')
        data['expiry_date_formatted'] = document.expiry_date.strftime('%d %B %Y')
        
        # Add expiry status
        from django.utils import timezone
        today = timezone.now().date()
        if document.expiry_date < today:
            data['status'] = 'expired'
        elif (document.expiry_date - today).days <= 30:
            data['status'] = 'expiring_soon'
        else:
            data['status'] = 'valid'
            
        return Response(data)

# Truck Management Views
class TruckViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TruckSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return Truck.objects.all()
        # Drivers can only see their assigned truck
        # Use the related_name from ForeignKey in UserProfile
        return Truck.objects.filter(userprofile__user=self.request.user)
    
    def perform_create(self, serializer):
        truck = serializer.save()
        # If the user is a driver, assign this truck to them
        if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'driver':
            profile = self.request.user.profile
            profile.assigned_truck = truck
            profile.save()

# Analytics Views
class AnalyticsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalyticsSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Get analytics for the last 6 months
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        return Analytics.objects.filter(
            user=user,
            month_year__gte=six_months_ago.strftime('%Y-%m')
        ).order_by('-month_year')

class AdminAnalyticsView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AnalyticsSerializer
    
    def get_queryset(self):
        # Get analytics for all users for the last 12 months
        one_year_ago = timezone.now() - datetime.timedelta(days=365)
        return Analytics.objects.filter(
            month_year__gte=one_year_ago.strftime('%Y-%m')
        ).order_by('-month_year')

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
        elif self.action in ['create', 'update', 'partial_update']:
            return OrderCreateUpdateSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        
        # Filter queryset based on user role
        if profile.role == 'admin':
            # Admins see all orders
            queryset = Order.objects.all()
        elif profile.role == 'driver':
            # Drivers see orders assigned to them
            queryset = Order.objects.filter(driver=user)
        else:
            # Customers see their own orders
            queryset = Order.objects.filter(customer=user)
        
        # Apply filters if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        # Update analytics
        self._update_analytics(order.customer, order)
    
    def perform_update(self, serializer):
        order = self.get_object()
        old_status = order.status
        updated_order = serializer.save()
        
        # If order status changed to completed, update analytics
        if old_status != 'completed' and updated_order.status == 'completed':
            self._update_analytics(updated_order.customer, updated_order)
    
    def _update_analytics(self, user, order):
        """Update analytics when order is created or completed"""
        today = timezone.now()
        month_year = today.strftime('%Y-%m')
        
        # Get or create analytics for this month
        analytics, created = Analytics.objects.get_or_create(
            user=user,
            month_year=month_year,
            defaults={
                'total_orders': 0,
                'completed_orders': 0,
                'total_distance': 0,
                'total_revenue': 0,
                'average_rating': 0
            }
        )
        
        # Update analytics
        if order.status == 'completed':
            analytics.completed_orders += 1
            # Calculate distance (you'll need to implement this based on your location data)
            distance = self._calculate_distance(order.origin, order.destination)
            analytics.total_distance += distance
            
            # Update driver's total kilometers if this is a driver's order
            if order.driver and hasattr(order.driver, 'profile'):
                profile = order.driver.profile
                profile.total_kilometers = (profile.total_kilometers or 0) + distance
                profile.save()
        
        analytics.total_orders += 1
        analytics.total_revenue += float(order.price)
        analytics.save()
    
    def _calculate_distance(self, origin, destination):
        """Calculate distance between two locations (simplified example)"""
        # This is a simplified example - you'll want to use a proper geocoding service
        # like Google Maps API or similar for accurate distance calculations
        return 100  # Placeholder value

# API for new orders available for drivers
class NewOrdersView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show new orders without a driver assigned
        if self.request.user.role == 'customer':
            return Order.objects.filter(
                status='new',
                driver__isnull=True  # No driver assigned yet
            ).order_by('-created_at')
        return Order.objects.none()
    
# Driver's orders API
class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        print(user.role)
        if user.role == 'driver':
            return Order.objects.filter(
                driver=user
            ).exclude(status='new').order_by('-created_at')
        
        # For customers, return ALL their orders including new ones
        return Order.objects.filter(
            customer=user
        ).order_by('-created_at')

# Delivery tracking API
class DeliveryTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryTrackingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return DeliveryTracking.objects.all()
        elif user.role == 'driver':
            # Drivers can see tracking for their orders
            return DeliveryTracking.objects.filter(order__driver=user)
        else:
            # Customers can see tracking for their orders
            return DeliveryTracking.objects.filter(order__customer=user)
    
    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        order = get_object_or_404(Order, id=order_id)
        
        # Verify the user has permission to track this order
        if not (self.request.user == order.driver or self.request.user == order.customer or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to track this order.")
        
        serializer.save()
        
        # Update order status if progress is 100%
        if serializer.validated_data.get('progress', 0) >= 100:
            order.status = 'completed'
            order.delivered_on = timezone.now()
            order.save()

# Get latest tracking info for an order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_tracking(request, order_id):
    order = get_object_or_404(Order, id=order_id)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order(request, pk):
    """Allow driver to accept an order"""
    try:
        order = Order.objects.get(pk=pk, status='new')
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found or no longer available'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify the user is a driver
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'driver':
        return Response(
            {'error': 'Only drivers can accept orders'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Update the order
    order.driver = request.user
    order.status = 'in-progress'
    order.save()
    
    # Update driver's profile if needed
    driver_profile = request.user.profile
    if not driver_profile.assigned_truck:
        # Assign the first available truck of the right type
        try:
            truck = Truck.objects.filter(
                truck_type=order.vehicle_type,
                is_active=True
            ).first()
            if truck:
                driver_profile.assigned_truck = truck
                driver_profile.save()
        except Exception as e:
            # Log the error but don't fail the order acceptance
            print(f"Error assigning truck: {str(e)}")
    
    return Response(
        {'status': 'Order accepted successfully'},
        status=status.HTTP_200_OK
    )

# Update order status
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    new_status = request.data.get('status')
    
    # Check permissions
    if not (request.user == order.driver or request.user == order.customer or request.user.is_staff):
        return Response(
            {"status": "error", "message": "You don't have permission to update this order"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if new_status and new_status in [status for status, _ in Order.STATUS_CHOICES]:
        # Additional validation for status transitions
        if new_status == 'completed' and order.status != 'in-progress':
            return Response(
                {"status": "error", "message": "Only orders in progress can be marked as completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = new_status
        if new_status == 'completed':
            order.delivered_on = timezone.now()
        order.save()
        
        # If this is a completion, update analytics
        if new_status == 'completed':
            analytics, _ = Analytics.objects.get_or_create(
                user=order.customer,
                month_year=timezone.now().strftime('%Y-%m'),
                defaults={
                    'total_orders': 0,
                    'completed_orders': 0,
                    'total_distance': 0,
                    'total_revenue': 0,
                    'average_rating': 0
                }
            )
            analytics.completed_orders += 1
            analytics.save()
        
        return Response({"status": "success", "message": f"Order status updated to {new_status}"})
    
    return Response({"status": "error", "message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
