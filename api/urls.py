from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Create a router for our ViewSets
router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'tracking', views.DeliveryTrackingViewSet, basename='tracking')
router.register(r'driver/documents', views.DriverDocumentViewSet, basename='driver-document')
router.register(r'trucks', views.TruckViewSet, basename='truck')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Authentication and user endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/driver/', views.DriverRegistrationView.as_view(), name='register-driver'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('driver/profile/', views.DriverProfileView.as_view(), name='driver-profile'),
    
    # Order-specific endpoints
    path('new-orders/', views.NewOrdersView.as_view(), name='new-orders'),
    path('new-orders/<int:pk>/accept/', views.accept_order, name='accept-order'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),
    
    # Analytics endpoints
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('admin/analytics/', views.AdminAnalyticsView.as_view(), name='admin-analytics'),
    
    # Tracking endpoint
    path('order-tracking/<str:order_id>/', views.get_order_tracking, name='order-tracking'),
    
    # Order status update
    path('update-order-status/<str:order_id>/', views.update_order_status, name='update-order-status'),
    
    # Include DRF auth URLs
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
