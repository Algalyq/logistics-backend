from django.contrib import admin
from .models import *

# Register your models here.
# Method 1: Using admin.site.register
admin.site.register(Order)
admin.site.register(Location)

# Alternative Method 2: Using decorators
'''
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'customer', 'driver', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'customer__first_name', 'customer__last_name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'latitude', 'longitude')
'''

admin.site.register(DeliveryTracking)