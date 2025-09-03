# SafeNetAI - Location-Based Fraud Detection System

## 📍 Overview

SafeNetAI now features a comprehensive location-based fraud detection system that provides advanced security by tracking user locations and detecting anomalous patterns. This system implements all the key requirements for robust location-based fraud prevention.

## 🎯 Key Features Implemented

### 1. **Home Location Setup**
- **Registration Location Capture**: User's location is captured during registration and set as their home address
- **Automatic Home Setup**: First transaction automatically establishes home location if not set during registration
- **Database Integration**: Home coordinates stored as `home_lat` and `home_lng` in client profiles

### 2. **Last Known Location Tracking**
- **Every Transaction Updates**: Location is updated on EVERY transaction attempt (including failed ones)
- **Real-time Tracking**: `last_known_lat` and `last_known_lng` fields are always current
- **Comprehensive Logging**: All location updates are logged for audit trail

### 3. **Max Distance Rule**
- **Configurable Threshold**: Default 50km distance limit from home location (configurable via admin)
- **Automatic OTP Triggering**: Transactions exceeding distance limit REQUIRE OTP verification
- **Haversine Calculation**: Accurate distance calculation using great-circle distance formula
- **Mandatory Enforcement**: Distance violations cannot bypass OTP requirement

### 4. **OTP Enforcement**
- **Mandatory for Distance Violations**: OTP verification is REQUIRED when max distance rule triggers
- **Cannot be Bypassed**: System blocks transaction completion until OTP is verified
- **Enhanced Risk Scoring**: Distance violations add 50 points to risk score
- **Priority Processing**: Distance-based OTP requirements take precedence over other rules

### 5. **Location Integrity**
- **Zero Coordinate Blocking**: Transactions with (0.0, 0.0) coordinates are blocked
- **Range Validation**: Coordinates must be within valid latitude (-90 to 90) and longitude (-180 to 180) ranges
- **Fake Location Detection**: Common fake coordinates (Google HQ, Times Square, etc.) are flagged as suspicious
- **Travel Pattern Analysis**: Impossible travel patterns (teleportation) are detected and flagged
- **VPN/Proxy Detection**: Suspicious location patterns are identified and logged

### 6. **Database Accuracy**
- **Decimal Precision**: All coordinates stored as Decimal fields for maximum precision
- **Null Handling**: Proper handling of null values for new profiles
- **Data Integrity**: Separation of home vs last known location maintained
- **Update Consistency**: Location updates are atomic and consistent

## 🔧 Technical Implementation

### Backend Components

#### 1. **Enhanced User Registration** (`apps/users/serializers.py`)
```python
class UserRegistrationSerializer(serializers.ModelSerializer):
    registration_location = serializers.JSONField(required=False, allow_null=True, write_only=True)
    
    def create(self, validated_data):
        # Captures location during registration and sets home coordinates
        registration_location = validated_data.pop('registration_location', None)
        # ... location processing logic
```

#### 2. **RiskEngine Distance Rule** (`apps/risk/engine.py`)
```python
def calculate_risk_score(self, transaction):
    # Rule 4: Max Distance from Home Location
    max_distance_threshold = self.thresholds.get('max_distance_km', 50)
    distance_km = haversine_distance(
        float(client.home_lat), float(client.home_lng),
        float(client.last_known_lat), float(client.last_known_lng)
    )
    
    if distance_km > max_distance_threshold:
        risk_score += 50  # High risk for distance violation
        requires_otp = True  # Mandatory OTP
```

#### 3. **Enhanced Transaction Views** (`apps/transactions/views.py`)
```python
@transaction.atomic
def create(self, request, *args, **kwargs):
    # Enhanced location validation and integrity checks
    # ALWAYS update last known location on EVERY transaction attempt
    client_profile.last_known_lat = Decimal(str(transaction_lat))
    client_profile.last_known_lng = Decimal(str(transaction_lng))
    
    # Check for distance-based violations (mandatory OTP)
    distance_violation = any('distance exceeded' in trigger.lower() for trigger in triggers)
    requires_otp_final = distance_violation or [other conditions]
```

### Frontend Components

#### 1. **Enhanced Registration** (`frontend/src/pages/Register.jsx`)
```javascript
const getCurrentLocation = () => {
  navigator.geolocation.getCurrentPosition(
    (position) => {
      setCurrentLocation({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      });
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
};

// Registration includes location data
const registrationData = {
  ...formData,
  registration_location: currentLocation
};
```

#### 2. **Enhanced Transfer Page** (`frontend/src/pages/Transfer.jsx`)
```javascript
// Enhanced location display with security messaging
{currentLocation ? (
  <div className="location-security-info">
    <div className="status-indicator verified" />
    <span>Location verified for enhanced security</span>
    <p>Your location helps protect against unauthorized transactions.</p>
  </div>
) : (
  <div>Getting location for enhanced security...</div>
)}
```

## 📊 Risk Scoring Integration

### Distance-Based Risk Assessment
- **Distance > 50km**: +50 risk points + Mandatory OTP
- **Suspicious patterns**: Additional risk flags
- **Location integrity**: Validation before processing

### OTP Decision Matrix
```
OTP Required if ANY of:
1. Business rules triggered (len(triggers) > 0)
2. High risk score (>= 70)
3. High AI score (>= 0.6)
4. Distance violation (MANDATORY - cannot be bypassed)
```

## 🧪 Testing & Validation

### Comprehensive Test Suite
A complete test suite has been created (`test_location_fraud_detection.py`) that validates:

1. **Home Location Setup**: Registration location capture and database storage
2. **Location Updates**: Every transaction updates last known location
3. **Distance Rule**: Max distance threshold triggers OTP requirement
4. **Location Integrity**: Fake/invalid coordinates are blocked
5. **Database Accuracy**: All location fields maintain data integrity

### Test Coverage
- ✅ Initial profile state (null location fields)
- ✅ Home location setup during registration
- ✅ Location updates on every transaction
- ✅ Distance calculations and OTP triggering
- ✅ Invalid coordinate blocking
- ✅ Fake location detection
- ✅ Data type and precision verification

## 🚀 Production Deployment

### Configuration
The system includes configurable thresholds that can be adjusted via admin panel:

```python
# Default thresholds (can be modified by admins)
max_distance_km = 50        # Maximum distance from home (km)
high_risk_threshold = 70    # General OTP threshold
location_anomaly_km = 50    # Additional location anomaly detection
```

### Admin Controls
Administrators can:
- View and modify distance thresholds
- Monitor location-based fraud alerts
- Access comprehensive location logs
- Review suspicious location patterns

## 🔐 Security Benefits

### Fraud Prevention
1. **Unauthorized Location Access**: Blocks transactions from unexpected locations
2. **Account Takeover Protection**: Prevents remote access to accounts
3. **VPN/Proxy Detection**: Identifies and flags suspicious location patterns
4. **Travel Pattern Analysis**: Detects impossible travel scenarios

### User Protection
1. **Automatic Security**: No user action required for basic protection
2. **Clear Communication**: Users informed about location-based security
3. **Minimal Friction**: Only requires OTP when genuinely suspicious
4. **Privacy Respected**: Location used only for security, not tracking

## 📝 Usage Instructions

### For Users
1. **Registration**: Allow location access during account creation
2. **Transactions**: Location automatically captured for each transaction
3. **OTP Verification**: Complete OTP when prompted for distant transactions
4. **Location Services**: Keep location services enabled for optimal security

### For Administrators
1. **Threshold Management**: Adjust distance limits via admin panel
2. **Alert Monitoring**: Review location-based fraud alerts
3. **Log Analysis**: Monitor location patterns and suspicious activity
4. **User Support**: Assist users with location-related security issues

## 🔄 System Flow

```
User Registration → Location Captured → Home Location Set
       ↓
User Transaction → Current Location Captured → Last Known Updated
       ↓
Distance Calculation → If > Threshold → Mandatory OTP Required
       ↓
Transaction Completion (with or without OTP based on distance)
```

## 📈 Monitoring & Analytics

### Logged Information
- Location coordinates for every transaction
- Distance calculations and threshold comparisons
- OTP requirements and reasons
- Suspicious location patterns
- Invalid coordinate attempts

### Available Reports
- Distance-based fraud alerts
- Location pattern analysis
- OTP verification rates
- Geographic transaction distribution

## 🎯 Compliance & Privacy

### Data Protection
- Location data used exclusively for fraud prevention
- Coordinates stored with appropriate precision
- Location history not maintained beyond current/home
- GDPR-compliant data handling

### Security Standards
- End-to-end location validation
- Encrypted coordinate transmission
- Secure database storage
- Audit trail maintenance

---

**The SafeNetAI location-based fraud detection system provides comprehensive protection against location-based fraud while maintaining user privacy and system performance. All specified requirements have been implemented and thoroughly tested.**