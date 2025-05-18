from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from api.models import UserProfile, Location, Order, DeliveryTracking

class Command(BaseCommand):
    help = 'Creates demo users and orders for the logistics app'

    def handle(self, *args, **options):
        # Ensure we have locations
        if Location.objects.count() == 0:
            self.stdout.write("No locations found. Please run 'python manage.py populate_locations' first.")
            return
            
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin1234')
            admin_user.save()
            UserProfile.objects.create(user=admin_user, role='admin')
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        
        # Create driver user
        driver_user, created = User.objects.get_or_create(
            username='driver',
            defaults={
                'email': 'driver@example.com',
                'first_name': 'Nurzhan',
                'last_name': 'A.',
            }
        )
        
        if created:
            driver_user.set_password('driver1234')
            driver_user.save()
            UserProfile.objects.create(user=driver_user, role='driver', phone='+7777-123-4567')
            self.stdout.write(self.style.SUCCESS(f'Created driver user: {driver_user.username}'))
        
        # Create customer user
        customer_user, created = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@example.com',
                'first_name': 'Kaysar',
                'last_name': 'Zhumabek',
            }
        )
        
        if created:
            customer_user.set_password('customer1234')
            customer_user.save()
            UserProfile.objects.create(user=customer_user, role='customer', phone='+7777-987-6543')
            self.stdout.write(self.style.SUCCESS(f'Created customer user: {customer_user.username}'))
            
        # Create some sample orders if none exist
        if Order.objects.count() == 0:
            self.create_sample_orders(customer_user, driver_user)
        else:
            self.stdout.write("Orders already exist in the database. Skipping order creation.")
    
    def create_sample_orders(self, customer, driver):
        locations = list(Location.objects.all())
        vehicle_types = [choice[0] for choice in Order.VEHICLE_CHOICES]
        product_types = [choice[0] for choice in Order.PRODUCT_CHOICES]
        weights = ['180kg', '320kg', '450kg', '620kg', '780kg']
        
        # Create new orders (not assigned to driver)
        for i in range(1, 6):
            origin, destination = random.sample(locations, 2)
            order = Order.objects.create(
                order_id=f'ORD-7895{i}',
                customer=customer,
                origin=origin,
                destination=destination,
                vehicle_type=random.choice(vehicle_types),
                product_type=random.choice(product_types),
                weight=random.choice(weights),
                price=random.randint(7, 15) * 100,
                status='new',
                created_at=timezone.now() - timedelta(days=random.randint(1, 5))
            )
            self.stdout.write(self.style.SUCCESS(f'Created new order: {order.order_id}'))
        
        # Create in-progress order
        in_progress_order = Order.objects.create(
            order_id='ORD-78901',
            customer=customer,
            driver=driver,
            origin=Location.objects.get(name='Almaty'),
            destination=Location.objects.get(name='Taraz'),
            vehicle_type='Truck',
            product_type='Construction',
            weight='780kg',
            price=1500,
            status='in-progress',
            created_at=timezone.now() - timedelta(days=4),
            estimated_arrival=timezone.now().date() + timedelta(days=1)
        )
        self.stdout.write(self.style.SUCCESS(f'Created in-progress order: {in_progress_order.order_id}'))
        
        # Create tracking point for in-progress order
        tracking = DeliveryTracking.objects.create(
            order=in_progress_order,
            latitude=43.06844,  # Somewhere between Almaty and Taraz
            longitude=74.13365,
            progress=45  # 45% of the way there
        )
        self.stdout.write(self.style.SUCCESS(f'Created tracking for order: {in_progress_order.order_id}'))
        
        # Create completed order
        completed_order = Order.objects.create(
            order_id='ORD-78845',
            customer=customer,
            driver=driver,
            origin=Location.objects.get(name='Kyzylorda'),
            destination=Location.objects.get(name='Almaty'),
            vehicle_type='Van',
            product_type='Clothing',
            weight='180kg',
            price=650,
            status='completed',
            created_at=timezone.now() - timedelta(days=7),
            estimated_arrival=timezone.now().date() - timedelta(days=2),
            delivered_on=timezone.now().date() - timedelta(days=2)
        )
        self.stdout.write(self.style.SUCCESS(f'Created completed order: {completed_order.order_id}'))
