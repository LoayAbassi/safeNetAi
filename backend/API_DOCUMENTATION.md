# SafeNetAi API Documentation

## Authentication

All API requests (except login and register) require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
http://localhost:8000
```

## Endpoints

### Authentication

#### Login
**POST** `/api/auth/login/`

**Request Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Register
**POST** `/api/auth/register/`

**Request Body:**
```json
{
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "national_id": "123456789"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Client Endpoints

#### Get Profile
**GET** `/api/client/profile/me/`

**Response:**
```json
{
    "id": 1,
    "full_name": "John Doe",
    "national_id": "123456789",
    "bank_account_number": "12345678",
    "balance": "5000.00",
    "risk_score": 0,
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### List Transactions
**GET** `/api/client/transactions/`

**Response:**
```json
[
    {
        "id": 1,
        "client": 1,
        "client_name": "John Doe",
        "amount": "1000.00",
        "transaction_type": "withdraw",
        "timestamp": "2024-01-01T10:00:00Z"
    }
]
```

#### Create Transaction
**POST** `/api/client/transactions/`

**Request Body:**
```json
{
    "amount": 15000.00,
    "transaction_type": "withdraw"
}
```

**Response:**
```json
{
    "id": 2,
    "client": 1,
    "client_name": "John Doe",
    "amount": "15000.00",
    "transaction_type": "withdraw",
    "timestamp": "2024-01-01T11:00:00Z"
}
```

#### List Fraud Alerts
**GET** `/api/client/fraud-alerts/`

**Response:**
```json
[
    {
        "id": 1,
        "transaction": 2,
        "transaction_details": {
            "id": 2,
            "client": 1,
            "client_name": "John Doe",
            "amount": "15000.00",
            "transaction_type": "withdraw",
            "timestamp": "2024-01-01T11:00:00Z"
        },
        "risk_level": "High",
        "message": "Fraud risk detected. Score: 75. Triggers: Large withdrawal: 15000.0 > 10000",
        "status": "Pending",
        "created_at": "2024-01-01T11:00:00Z"
    }
]
```

### Admin Endpoints

#### List Clients
**GET** `/api/admin/clients/`

**Response:**
```json
[
    {
        "id": 1,
        "full_name": "John Doe",
        "national_id": "123456789",
        "bank_account_number": "12345678",
        "balance": "5000.00",
        "risk_score": 75,
        "user_username": "johndoe",
        "user_email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### Create Client
**POST** `/api/admin/clients/`

**Request Body:**
```json
{
    "full_name": "New Client",
    "national_id": "111222333",
    "bank_account_number": "11111111",
    "balance": 10000.00
}
```

#### Search Clients
**GET** `/api/admin/clients/search/?q=john`

**Response:**
```json
[
    {
        "id": 1,
        "full_name": "John Doe",
        "national_id": "123456789",
        "bank_account_number": "12345678",
        "balance": "5000.00",
        "risk_score": 75,
        "user_username": "johndoe",
        "user_email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### List All Transactions
**GET** `/api/admin/transactions/`

**Response:**
```json
[
    {
        "id": 1,
        "client_name": "John Doe",
        "client_national_id": "123456789",
        "amount": "1000.00",
        "transaction_type": "withdraw",
        "timestamp": "2024-01-01T10:00:00Z"
    }
]
```

#### Search Transactions
**GET** `/api/admin/transactions/search/?q=john`

#### List Fraud Alerts
**GET** `/api/admin/fraud-alerts/`

**Response:**
```json
[
    {
        "id": 1,
        "transaction_details": {
            "id": 2,
            "client_name": "John Doe",
            "client_national_id": "123456789",
            "amount": "15000.00",
            "transaction_type": "withdraw",
            "timestamp": "2024-01-01T11:00:00Z"
        },
        "risk_level": "High",
        "message": "Fraud risk detected. Score: 75. Triggers: Large withdrawal: 15000.0 > 10000",
        "status": "Pending",
        "created_at": "2024-01-01T11:00:00Z"
    }
]
```

#### Update Fraud Alert Status
**PATCH** `/api/admin/fraud-alerts/{id}/update_status/`

**Request Body:**
```json
{
    "status": "Reviewed"
}
```

#### List Thresholds
**GET** `/api/admin/thresholds/`

**Response:**
```json
[
    {
        "id": 1,
        "key": "LARGE_WITHDRAWAL_AMOUNT",
        "value": 10000.0,
        "description": "Amount threshold for large withdrawals"
    }
]
```

#### Create/Update Threshold
**POST** `/api/admin/thresholds/`

**Request Body:**
```json
{
    "key": "LARGE_WITHDRAWAL_AMOUNT",
    "value": 15000.0,
    "description": "Updated amount threshold for large withdrawals"
}
```

#### List Rules
**GET** `/api/admin/rules/`

**Response:**
```json
[
    {
        "id": 1,
        "key": "large_withdrawal_rule",
        "description": "Flag large withdrawals as potentially risky",
        "enabled": true,
        "params_json": {
            "threshold": 10000
        }
    }
]
```

#### Create/Update Rule
**POST** `/api/admin/rules/`

**Request Body:**
```json
{
    "key": "new_rule",
    "description": "New fraud detection rule",
    "enabled": true,
    "params_json": {
        "param1": "value1"
    }
}
```

## Error Responses

### Validation Error
**Status:** 400 Bad Request
```json
{
    "field_name": [
        "This field is required."
    ]
}
```

### Authentication Error
**Status:** 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Permission Error
**Status:** 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Not Found Error
**Status:** 404 Not Found
```json
{
    "detail": "Not found."
}
```

## Transaction Types

- `deposit` - Money deposited into account
- `withdraw` - Money withdrawn from account
- `transfer` - Money transferred between accounts

## Risk Levels

- `Low` - 0-39 risk points
- `Medium` - 40-69 risk points
- `High` - 70+ risk points

## Fraud Alert Status

- `Pending` - Alert created, awaiting review
- `Reviewed` - Alert has been reviewed by admin

## Testing with curl

### Login and get token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access'
```

### Use token for authenticated requests
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access')

curl -X GET http://localhost:8000/api/admin/clients/ \
  -H "Authorization: Bearer $TOKEN"
```
