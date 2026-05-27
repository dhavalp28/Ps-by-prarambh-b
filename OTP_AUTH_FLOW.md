# OTP-Based Authentication Flow

This document describes the new OTP-based authentication system implemented in the backend.

## Overview

The system uses One-Time Passwords (OTP) for both registration and login, eliminating the need for password management. Users receive OTPs via SMS/Email and verify their phone numbers during registration.

## Database Models

### User Model
```python
- id: Integer (Primary Key)
- first_name: String
- last_name: String
- email: String (Unique)
- phone: String (Unique)
- state_id: Integer (Foreign Key)
- city_id: Integer (Foreign Key)
- referral_code: String (Optional)
- hashed_password: String (Nullable - for OTP-only login)
- is_phone_verified: Boolean (Default: False)
- created_at: DateTime
- updated_at: DateTime
```

### OtpSession Model
```python
- id: Integer (Primary Key)
- phone: String (Indexed)
- otp: String
- purpose: String ('register' or 'login')
- temp_user_data: String (JSON - stores temporary registration data)
- expires_at: DateTime (Default: 10 minutes from creation)
- attempts: Integer (Default: 0, Max: 5)
- is_verified: Boolean (Default: False)
- created_at: DateTime
- updated_at: DateTime
```

## API Endpoints

### 1. Registration Flow

#### POST /auth/register/init
**Purpose**: Initialize registration - validate user data and send OTP

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "state_id": 1,
  "city_id": 5,
  "referral_code": "REF123" (optional)
}
```

**Response** (Success):
```json
{
  "response": true,
  "title": "Registration Initiated",
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:30:00"
  },
  "message": "OTP sent successfully. Please verify within 10 minutes.",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Register Init",
  "data": null,
  "message": null,
  "error": "Phone already registered"
}
```

**Validations**:
- Phone must not be already registered
- Email must not be already registered
- State must exist
- City must exist and belong to the selected state

---

#### POST /auth/register/verify
**Purpose**: Verify OTP and create user account

**Request Body**:
```json
{
  "otp_session_id": 123,
  "otp": "654321"
}
```

**Response** (Success):
```json
{
  "response": true,
  "title": "Registration Successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+919876543210",
      "is_phone_verified": true
    }
  },
  "message": "User registered and verified successfully",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Register Verify",
  "data": null,
  "message": null,
  "error": "Invalid OTP. Please try again."
}
```

**Validations**:
- OTP session must exist
- OTP must not be expired (10 minutes)
- Maximum 5 OTP attempts allowed
- OTP must match (or be "123456" for development)

---

### 2. Login Flow

#### POST /auth/login/send-otp
**Purpose**: Send OTP for login

**Request Body**:
```json
{
  "phone": "+919876543210"
}
```

**Response** (Success):
```json
{
  "response": true,
  "title": "OTP Sent",
  "data": {
    "otp_session_id": 124,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:35:00"
  },
  "message": "OTP sent successfully. Please verify within 10 minutes.",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Login Send OTP",
  "data": null,
  "message": null,
  "error": "User not found. Please register first."
}
```

**Validations**:
- User must exist with the given phone
- User's phone must be verified

---

#### POST /auth/login/verify
**Purpose**: Verify OTP and login user

**Request Body**:
```json
{
  "otp_session_id": 124,
  "otp": "654321"
}
```

**Response** (Success):
```json
{
  "response": true,
  "title": "Login Successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+919876543210",
      "is_phone_verified": true
    }
  },
  "message": "Login successful",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Login Verify",
  "data": null,
  "message": null,
  "error": "OTP has expired. Please request a new one."
}
```

**Validations**:
- OTP session must exist
- OTP must not be expired (10 minutes)
- Maximum 5 OTP attempts allowed
- OTP must match (or be "123456" for development)

---

### 3. Resend OTP

#### POST /auth/resend-otp
**Purpose**: Resend OTP - invalidates old OTP and generates new one

**Request Body**:
```json
{
  "otp_session_id": 123
}
```

**Response** (Success):
```json
{
  "response": true,
  "title": "OTP Resent",
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:40:00"
  },
  "message": "New OTP sent successfully. Please verify within 10 minutes.",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Resend OTP",
  "data": null,
  "message": null,
  "error": "OTP session not found"
}
```

**Behavior**:
- Invalidates the old OTP
- Generates a new OTP
- Resets attempt counter to 0
- Extends expiry time by 10 minutes

---

### 4. Update Phone Number During Registration

#### POST /auth/update-phone
**Purpose**: Update phone number during registration - invalidates old OTP and generates new one

**Request Parameters**:
- `otp_session_id`: Integer (query parameter)
- `new_phone`: String (query parameter)

**Response** (Success):
```json
{
  "response": true,
  "title": "Phone Updated",
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543211",
    "expires_at": "2024-05-27T15:45:00"
  },
  "message": "OTP sent to new phone number. Please verify within 10 minutes.",
  "error": null
}
```

**Response** (Error):
```json
{
  "response": false,
  "title": "Update Phone",
  "data": null,
  "message": null,
  "error": "Phone number already registered"
}
```

**Behavior**:
- Updates the phone number in the OTP session
- Invalidates the old OTP
- Generates a new OTP for the new phone number
- Resets attempt counter to 0
- Can only be done before OTP verification

---

## OTP Verification Logic

### Development Mode (is_development = True)
```python
if entered_otp == "123456" or entered_otp == real_otp:
    verify_user = True
```

### Production Mode (is_development = False)
```python
if entered_otp == real_otp:
    verify_user = True
```

**⚠️ Important**: The "123456" bypass is ONLY for development/testing. Remove it in production by setting `is_development = False` in `services/otp_auth_service.py`.

---

## OTP Generation

- **Length**: 6 digits
- **Format**: Random numeric string (0-9)
- **Expiry**: 10 minutes from creation
- **Max Attempts**: 5 attempts per OTP session
- **Resend**: Generates new OTP, resets attempts

---

## Registration Flow Diagram

```
1. User submits registration data
   ↓
2. POST /auth/register/init
   - Validate user data
   - Check phone/email uniqueness
   - Generate OTP
   - Store temporary user data
   - Return otp_session_id
   ↓
3. User receives OTP (SMS/Email)
   ↓
4. User enters OTP
   ↓
5. POST /auth/register/verify
   - Verify OTP
   - Create user account
   - Mark phone as verified
   - Return access token
   ↓
6. User is registered and logged in
```

---

## Login Flow Diagram

```
1. User enters phone number
   ↓
2. POST /auth/login/send-otp
   - Check if user exists
   - Check if phone is verified
   - Generate OTP
   - Return otp_session_id
   ↓
3. User receives OTP (SMS/Email)
   ↓
4. User enters OTP
   ↓
5. POST /auth/login/verify
   - Verify OTP
   - Return access token
   ↓
6. User is logged in
```

---

## Phone Number Change During Registration

```
1. User is in registration flow with otp_session_id
   ↓
2. User wants to change phone number
   ↓
3. POST /auth/update-phone?otp_session_id=123&new_phone=+919876543211
   - Validate new phone is not registered
   - Update phone in OTP session
   - Invalidate old OTP
   - Generate new OTP for new phone
   - Reset attempts
   ↓
4. User receives OTP on new phone
   ↓
5. User enters new OTP
   ↓
6. POST /auth/register/verify
   - Verify OTP
   - Create user with new phone
   - Return access token
```

---

## Error Handling

### Common Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Phone already registered | 400 | User tried to register with existing phone | Use login instead |
| Email already registered | 400 | User tried to register with existing email | Use different email |
| State not found | 404 | Invalid state_id | Verify state_id exists |
| City not found | 404 | Invalid city_id | Verify city_id exists |
| City does not belong to state | 400 | city_id doesn't match state_id | Select city from correct state |
| OTP session not found | 404 | Invalid otp_session_id | Request new OTP |
| OTP has expired | 400 | OTP older than 10 minutes | Use resend-otp endpoint |
| Invalid OTP | 400 | Wrong OTP entered | Check OTP and try again |
| Maximum OTP attempts exceeded | 400 | More than 5 failed attempts | Use resend-otp endpoint |
| User not found | 404 | Phone not registered | Register first |
| Phone number not verified | 400 | User hasn't completed registration | Complete registration |

---

## Security Considerations

1. **OTP Expiry**: OTPs expire after 10 minutes
2. **Attempt Limiting**: Maximum 5 attempts per OTP session
3. **Phone Verification**: Users must verify phone during registration
4. **Temporary Data**: User data is stored temporarily until OTP verification
5. **Development Bypass**: "123456" bypass is only for development - MUST be removed in production
6. **Token Security**: Access tokens are JWT-based with configurable expiry

---

## Implementation Notes

### Files Modified/Created

**New Files**:
- `db/models/otp_session.py` - OtpSession model
- `repositories/otp_session_repository.py` - OTP session repository
- `services/otp_auth_service.py` - OTP authentication service
- `OTP_AUTH_FLOW.md` - This documentation

**Modified Files**:
- `db/models/user.py` - Added `is_phone_verified` field, made `hashed_password` nullable
- `db/models/init.py` - Added OtpSession import
- `schemas/auth.py` - Added new schemas for OTP flow
- `routers/routes/auth.py` - Added new OTP endpoints
- `core/otp.py` - Enhanced OTP generation and verification

### TODO Items

1. **SMS/Email Integration**: Implement actual OTP sending via SMS/Email service
   - Replace TODO comments in `services/otp_auth_service.py`
   - Integrate with Twilio, AWS SNS, or similar service

2. **Production Deployment**:
   - Set `is_development = False` in `services/otp_auth_service.py`
   - Remove OTP from response (currently returned for testing)
   - Configure SMS/Email service credentials

3. **Database Migration**:
   - Run Alembic migration to create `otp_sessions` table
   - Add `is_phone_verified` column to `users` table
   - Make `hashed_password` nullable in `users` table

4. **Frontend Integration**:
   - Implement registration flow UI
   - Implement login flow UI
   - Handle OTP session management
   - Implement phone number change flow

---

## Testing

### Test Registration Flow
```bash
# 1. Initialize registration
curl -X POST http://localhost:8000/auth/register/init \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+919876543210",
    "state_id": 1,
    "city_id": 5
  }'

# Response will include otp_session_id and otp (for testing)

# 2. Verify OTP
curl -X POST http://localhost:8000/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "otp_session_id": 123,
    "otp": "123456"
  }'
```

### Test Login Flow
```bash
# 1. Send OTP
curl -X POST http://localhost:8000/auth/login/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210"
  }'

# Response will include otp_session_id and otp (for testing)

# 2. Verify OTP
curl -X POST http://localhost:8000/auth/login/verify \
  -H "Content-Type: application/json" \
  -d '{
    "otp_session_id": 124,
    "otp": "123456"
  }'
```

---

## Backward Compatibility

The old password-based authentication endpoints are still available:
- `POST /auth/register` - Legacy registration with password
- `POST /auth/login` - Legacy login with password

These can be deprecated in future versions once all clients migrate to OTP-based flow.
