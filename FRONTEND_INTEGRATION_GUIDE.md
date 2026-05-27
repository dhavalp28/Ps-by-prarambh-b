# Frontend Integration Guide - OTP Authentication

## Overview

This guide explains which API endpoints to call for each use case in the OTP authentication flow.

## API Base URL

```
Development: http://localhost:8000
Production: https://api.example.com (update with actual URL)
```

## Authentication Header

All authenticated requests must include:
```
Authorization: Bearer {access_token}
```

---

## Registration Flow

### Step 1: Load States (On Page Load)

**When**: Page loads or user navigates to registration

**API Call**:
```
GET /states
```

**Response**: List of all states with id and name

**Use**: Populate state dropdown

---

### Step 2: Load Cities (When State Selected)

**When**: User selects a state

**API Call**:
```
GET /cities?state_id={state_id}
```

**Response**: List of cities for the selected state

**Use**: Populate city dropdown

---

### Step 3: Send Registration OTP

**When**: User fills registration form and clicks "Send OTP"

**API Call**:
```
POST /auth/register/init
```

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

**Response**:
```json
{
  "response": true,
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:30:00"
  }
}
```

**Use**: 
- Save `otp_session_id` for next step
- Show OTP input screen
- Start 10-minute timer using `expires_at`

**Errors**:
- "Phone already registered" → Show login option
- "Email already registered" → Use different email
- "State not found" → Validate state selection
- "City not found" → Validate city selection

---

### Step 4: Verify Registration OTP

**When**: User enters OTP and clicks "Verify"

**API Call**:
```
POST /auth/register/verify
```

**Request Body**:
```json
{
  "otp_session_id": 123,
  "otp": "654321"
}
```

**Response**:
```json
{
  "response": true,
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
  }
}
```

**Use**:
- Save `access_token` to localStorage
- Save `user` info to localStorage
- Redirect to dashboard

**Errors**:
- "Invalid OTP" → Show error, allow retry
- "OTP has expired" → Show "Resend OTP" button
- "Maximum OTP attempts exceeded" → Show "Resend OTP" button

---

### Step 5: Resend Registration OTP

**When**: User clicks "Resend OTP" button

**API Call**:
```
POST /auth/resend-otp
```

**Request Body**:
```json
{
  "otp_session_id": 123
}
```

**Response**:
```json
{
  "response": true,
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:40:00"
  }
}
```

**Use**:
- Clear OTP input field
- Restart timer with new `expires_at`
- Show success message

---

### Step 6: Change Phone Number During Registration

**When**: User clicks "Change Phone Number" button

**API Call**:
```
POST /auth/update-phone?otp_session_id={otp_session_id}&new_phone={new_phone}
```

**Response**:
```json
{
  "response": true,
  "data": {
    "otp_session_id": 123,
    "phone": "+919876543211",
    "expires_at": "2024-05-27T15:45:00"
  }
}
```

**Use**:
- Clear OTP input field
- Update displayed phone number
- Restart timer with new `expires_at`
- Show success message

**Errors**:
- "Phone number already registered" → Show error

---

## Login Flow

### Step 1: Send Login OTP

**When**: User enters phone and clicks "Send OTP"

**API Call**:
```
POST /auth/login/send-otp
```

**Request Body**:
```json
{
  "phone": "+919876543210"
}
```

**Response**:
```json
{
  "response": true,
  "data": {
    "otp_session_id": 124,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:35:00"
  }
}
```

**Use**:
- Save `otp_session_id` for next step
- Show OTP input screen
- Start 10-minute timer using `expires_at`

**Errors**:
- "User not found" → Show registration option
- "Phone number not verified" → Show registration option

---

### Step 2: Verify Login OTP

**When**: User enters OTP and clicks "Verify"

**API Call**:
```
POST /auth/login/verify
```

**Request Body**:
```json
{
  "otp_session_id": 124,
  "otp": "654321"
}
```

**Response**:
```json
{
  "response": true,
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
  }
}
```

**Use**:
- Save `access_token` to localStorage
- Save `user` info to localStorage
- Redirect to dashboard

**Errors**:
- "Invalid OTP" → Show error, allow retry
- "OTP has expired" → Show "Resend OTP" button
- "Maximum OTP attempts exceeded" → Show "Resend OTP" button

---

### Step 3: Resend Login OTP

**When**: User clicks "Resend OTP" button

**API Call**:
```
POST /auth/resend-otp
```

**Request Body**:
```json
{
  "otp_session_id": 124
}
```

**Response**:
```json
{
  "response": true,
  "data": {
    "otp_session_id": 124,
    "phone": "+919876543210",
    "expires_at": "2024-05-27T15:40:00"
  }
}
```

**Use**:
- Clear OTP input field
- Restart timer with new `expires_at`
- Show success message

---

## Token Management

### Store Token After Login/Registration

**When**: Receive `access_token` from login or registration

**Action**:
```
localStorage.setItem('access_token', access_token)
localStorage.setItem('user', JSON.stringify(user))
```

---

### Use Token in Authenticated Requests

**When**: Making any API request that requires authentication

**Action**: Add header to all requests:
```
Authorization: Bearer {access_token}
```

---

### Handle Token Expiry

**When**: API returns 401 Unauthorized

**Action**:
```
localStorage.removeItem('access_token')
localStorage.removeItem('user')
Redirect to login page
```

---

### Logout

**When**: User clicks logout

**Action**:
```
localStorage.removeItem('access_token')
localStorage.removeItem('user')
Redirect to login page
```

---

## Error Handling

### Common Errors and User Messages

| Error | User Message |
|-------|--------------|
| "Phone already registered" | "This phone is already registered. Please login instead." |
| "Email already registered" | "This email is already registered. Please use a different email." |
| "OTP has expired" | "OTP expired. Click 'Resend OTP' to get a new one." |
| "Invalid OTP" | "Incorrect OTP. Please try again." |
| "Maximum OTP attempts exceeded" | "Too many failed attempts. Click 'Resend OTP' to try again." |
| "User not found" | "Phone number not registered. Please register first." |
| "State not found" | "Selected state is invalid. Please select a valid state." |
| "City not found" | "Selected city is invalid. Please select a valid city." |
| "City does not belong to the selected state" | "Selected city does not belong to the selected state." |

---

## Response Format

All API responses follow this format:

```json
{
  "response": true/false,
  "title": "Operation Title",
  "data": {...} or null,
  "message": "Success/Info message" or null,
  "error": "Error message" or null
}
```

**Check**: Always check `response` field
- `true` = Success, use `data`
- `false` = Error, use `error`

---

## Development Testing

### Test OTP
Use `123456` as OTP for any session during development.

### Test Phone Numbers
- `+919876543210`
- `+919876543211`

### Test States/Cities
```
GET /states → Get all states
GET /cities?state_id=1 → Get cities for state 1
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/states` | GET | Get all states |
| `/cities?state_id=X` | GET | Get cities for state |
| `/auth/register/init` | POST | Send registration OTP |
| `/auth/register/verify` | POST | Verify OTP and create user |
| `/auth/login/send-otp` | POST | Send login OTP |
| `/auth/login/verify` | POST | Verify OTP and login |
| `/auth/resend-otp` | POST | Resend OTP |
| `/auth/update-phone` | POST | Update phone during registration |

---

## Implementation Checklist

### Registration
- [ ] Load states on page load
- [ ] Load cities when state selected
- [ ] Call `/auth/register/init` on "Send OTP"
- [ ] Show OTP input screen
- [ ] Start timer with `expires_at`
- [ ] Call `/auth/register/verify` on "Verify"
- [ ] Save token to localStorage
- [ ] Redirect to dashboard
- [ ] Show "Resend OTP" button
- [ ] Show "Change Phone" button

### Login
- [ ] Call `/auth/login/send-otp` on "Send OTP"
- [ ] Show OTP input screen
- [ ] Start timer with `expires_at`
- [ ] Call `/auth/login/verify` on "Verify"
- [ ] Save token to localStorage
- [ ] Redirect to dashboard
- [ ] Show "Resend OTP" button

### Token Management
- [ ] Store token in localStorage
- [ ] Include token in authenticated requests
- [ ] Handle 401 responses
- [ ] Implement logout

### Error Handling
- [ ] Display user-friendly error messages
- [ ] Handle network errors
- [ ] Handle timeout errors
- [ ] Show retry options

---

## Support

For questions:
1. Check the API endpoint details above
2. Review error messages and solutions
3. Check response format
4. Contact backend team
