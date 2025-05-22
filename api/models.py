from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

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
    customer = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='customer_orders')
    driver = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_orders')
    
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

class DriverDocument(models.Model):
    DOCUMENT_TYPES = [
        ('id_card', 'ID Card'),
        ('driver_license', 'Driver\'s License'),
        ('truck_license', 'Truck License'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='documents', null=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='driver_documents/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.document_number}"

class Truck(models.Model):
    TRUCK_TYPES = [
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('refrigerated', 'Refrigerated Truck'),
        ('tanker', 'Tanker'),
    ]
    
    license_plate = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    truck_type = models.CharField(max_length=20, choices=TRUCK_TYPES)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    length = models.DecimalField(max_digits=6, decimal_places=2)  # in meters
    tachograph_expiry = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.license_plate} - {self.model} ({self.year})"

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.role}"

class UserProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ], default='customer')
    
    # Driver specific fields
    experience_years = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_kilometers = models.PositiveIntegerField(default=0, null=True, blank=True)
    documents = models.ManyToManyField(DriverDocument, blank=True)
    assigned_truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Analytics(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='analytics')
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    total_distance = models.FloatField(default=0)  # in kilometers
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    month_year = models.CharField(max_length=7)  # Format: YYYY-MM
    
    class Meta:
        verbose_name_plural = 'Analytics'
        unique_together = ('user', 'month_year')
    
    def __str__(self):
        return f"{self.user.username} - {self.month_year}"
