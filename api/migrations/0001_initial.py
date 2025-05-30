# Generated by Django 4.2.21 on 2025-05-22 09:04

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('customer', 'Customer'), ('driver', 'Driver'), ('admin', 'Admin')], default='customer', max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DriverDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('id_card', 'ID Card'), ('driver_license', "Driver's License"), ('truck_license', 'Truck License'), ('other', 'Other')], max_length=20)),
                ('document_number', models.CharField(max_length=100)),
                ('issue_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='driver_documents/')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_plate', models.CharField(max_length=20, unique=True)),
                ('model', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
                ('truck_type', models.CharField(choices=[('truck', 'Truck'), ('van', 'Van'), ('refrigerated', 'Refrigerated Truck'), ('tanker', 'Tanker')], max_length=20)),
                ('max_weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('length', models.DecimalField(decimal_places=2, max_digits=6)),
                ('tachograph_expiry', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.CharField(choices=[('customer', 'Customer'), ('driver', 'Driver'), ('admin', 'Admin')], default='customer', max_length=20)),
                ('experience_years', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('total_kilometers', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('assigned_truck', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.truck')),
                ('documents', models.ManyToManyField(blank=True, to='api.driverdocument')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=20, unique=True)),
                ('vehicle_type', models.CharField(choices=[('Truck', 'Truck'), ('Van', 'Van'), ('Refrigerated', 'Refrigerated')], max_length=20)),
                ('product_type', models.CharField(choices=[('Electronics', 'Electronics'), ('Food', 'Food'), ('Furniture', 'Furniture'), ('Construction', 'Construction'), ('Pharmaceuticals', 'Pharmaceuticals'), ('Clothing', 'Clothing')], max_length=20)),
                ('weight', models.CharField(max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('new', 'New'), ('in-progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='new', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estimated_arrival', models.DateField(blank=True, null=True)),
                ('delivered_on', models.DateField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_orders', to=settings.AUTH_USER_MODEL)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_orders', to='api.location')),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='driver_orders', to=settings.AUTH_USER_MODEL)),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_orders', to='api.location')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('progress', models.IntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_points', to='api.order')),
            ],
        ),
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_orders', models.PositiveIntegerField(default=0)),
                ('completed_orders', models.PositiveIntegerField(default=0)),
                ('total_distance', models.FloatField(default=0)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('average_rating', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('month_year', models.CharField(max_length=7)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Analytics',
                'unique_together': {('user', 'month_year')},
            },
        ),
    ]
