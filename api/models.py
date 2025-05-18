from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    VEHICLE_CHOICES = [
        ('Truck', 'Truck'),
        ('Van', 'Van'),
        ('Refrigerated', 'Refrigerated'),
    ]
    
    PRODUCT_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Food', 'Food'),
        ('Furniture', 'Furniture'),
        ('Construction', 'Construction'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Clothing', 'Clothing'),
    ]
    
    # Order identification
    order_id = models.CharField(max_length=20, unique=True)  # ORD-XXXXX format
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_orders')
    
    # Locations
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='origin_orders')
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='destination_orders')
    
    # Details
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES)
    weight = models.CharField(max_length=20)  # Format "450kg"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_arrival = models.DateField(null=True, blank=True)
    delivered_on = models.DateField(null=True, blank=True)
    
    # Cancellation reason if applicable
    reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.order_id} - {self.customer.username} ({self.status})"

class DeliveryTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # 0-100%
    
    def __str__(self):
        return f"Tracking for {self.order.order_id} at {self.timestamp} - {self.progress}%"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ], default='customer')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
