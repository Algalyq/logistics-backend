from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for our ViewSets
router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'tracking', views.DeliveryTrackingViewSet, basename='tracking')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Authentication and user endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Order-specific endpoints
    path('new-orders/', views.NewOrdersView.as_view(), name='new-orders'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),
    
    # Tracking endpoint
    path('order-tracking/<str:order_id>/', views.get_order_tracking, name='order-tracking'),
    
    # Order status update
    path('update-order-status/<str:order_id>/', views.update_order_status, name='update-order-status'),
    
    # Include DRF auth URLs
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
