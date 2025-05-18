# Logistics Backend API

This Django REST API serves as the backend for the Logistics React Native mobile application. It provides endpoints for user authentication, order management, and real-time tracking.

## Setup

1. **Activate the virtual environment**

```bash
source venv/bin/activate
```

2. **Run the Django server**

```bash
python manage.py runserver 0.0.0.0:8000
```

This will start the server at http://localhost:8000 and make it accessible over your local network.

## API Endpoints

### Authentication

- `POST /api/register/` - Register a new user
- `POST /api-token-auth/` - Get authentication token

### Order Management

- `GET /api/orders/` - List all orders (filtered based on user role)
- `POST /api/orders/` - Create a new order
- `GET /api/orders/<id>/` - Get order details
- `PUT/PATCH /api/orders/<id>/` - Update an order
- `DELETE /api/orders/<id>/` - Delete an order
- `GET /api/new-orders/` - List new orders available for drivers
- `GET /api/my-orders/` - List current user's orders (excluding new orders)

### Tracking

- `GET /api/order-tracking/<order_id>/` - Get the latest tracking info for an order
- `POST /api/update-order-status/<order_id>/` - Update order status

### Locations

- `GET /api/locations/` - List all Kazakhstan locations with GPS coordinates

## Demo Accounts

The system is pre-populated with these demo accounts:

### Admin
- Username: admin
- Password: admin1234

### Driver
- Username: driver
- Password: driver1234

### Customer
- Username: customer
- Password: customer1234

## Connecting to React Native App

To connect your React Native app to this backend:

1. Update your API service in React Native to point to this Django backend instead of using mock data
2. Add authentication token handling in your API requests
3. Convert your mock data functions to use real API endpoints

### Example API Configuration for React Native

```javascript
// api/config.js
export const API_URL = 'http://YOUR_LOCAL_IP:8000';

// api/client.js
import { API_URL } from './config';

const apiClient = {
  token: null,
  
  setToken(token) {
    this.token = token;
  },
  
  async login(username, password) {
    const response = await fetch(`${API_URL}/api-token-auth/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      throw new Error('Authentication failed');
    }
    
    const data = await response.json();
    this.setToken(data.token);
    return data;
  },
  
  async get(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        'Authorization': `Token ${this.token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    return response.json();
  },
  
  async post(endpoint, data) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${this.token}`,
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    return response.json();
  },
  
  // Add other methods as needed (put, delete, etc.)
};

export default apiClient;
```

Then you can use this client in your React Native app:

```javascript
import apiClient from '../api/client';

// In your login screen
const handleLogin = async () => {
  try {
    await apiClient.login(username, password);
    router.replace('/(tabs)');
  } catch (error) {
    // Handle error
  }
};

// In your orders screen
const fetchOrders = async () => {
  try {
    const orders = await apiClient.get('/api/orders/');
    setOrders(orders);
  } catch (error) {
    // Handle error
  }
};
```
