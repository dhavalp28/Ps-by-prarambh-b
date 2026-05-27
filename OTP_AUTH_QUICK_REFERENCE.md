# OTP Authentication - Quick Reference for Frontend

## Quick Start

### Registration (3 Steps)

**Step 1: Send OTP**
```
POST /auth/register/init
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+919876543210",
  "state_id": 1,
  "city_id": 5,
  "referral_code": "REF123" (optional)
}

Response:
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

**Step 2: User enters OTP (from SMS/Email)**

**Step 3: Verify OTP**
```
POST /auth/register/verify
Content-Type: application/json

{
  "otp_session_id": 123,
  "otp": "654321"
}

Response:
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

---

### Login (2 Steps)

**Step 1: Send OTP**
```
POST /auth/login/send-otp
Content-Type: application/json

{
  "phone": "+919876543210"
}

Response:
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

**Step 2: Verify OTP**
```
POST /auth/login/verify
Content-Type: application/json

{
  "otp_session_id": 124,
  "otp": "654321"
}

Response:
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

---

## Additional Features

### Resend OTP
```
POST /auth/resend-otp
Content-Type: application/json

{
  "otp_session_id": 123
}

Response:
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

### Change Phone Number During Registration
```
POST /auth/update-phone?otp_session_id=123&new_phone=%2B919876543211
Content-Type: application/json

Response:
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

---

## Important Notes

### Development Testing
- **Test OTP**: Use `123456` as OTP for testing (works with any otp_session_id)
- **Real OTP**: Check response data for `otp` field (only in development)

### Production
- Remove `123456` bypass
- OTP will be sent via SMS/Email only
- OTP will NOT be returned in response

### Error Handling
| Error | What to do |
|-------|-----------|
| "Phone already registered" | Show: "This phone is already registered. Please login instead." |
| "Email already registered" | Show: "This email is already registered. Please use a different email." |
| "OTP has expired" | Show: "OTP expired. Click 'Resend OTP' to get a new one." |
| "Invalid OTP" | Show: "Incorrect OTP. Please try again." |
| "Maximum OTP attempts exceeded" | Show: "Too many failed attempts. Click 'Resend OTP' to try again." |
| "User not found" | Show: "Phone number not registered. Please register first." |

---

## Frontend Implementation Checklist

### Registration Screen
- [ ] Input fields: First Name, Last Name, Email, Phone, State, City, Referral Code (optional)
- [ ] Call `/auth/register/init` on "Send OTP" button
- [ ] Store `otp_session_id` from response
- [ ] Show OTP input screen with timer (10 minutes)
- [ ] Show "Resend OTP" button (after 30 seconds)
- [ ] Show "Change Phone Number" option
- [ ] Call `/auth/register/verify` on "Verify" button
- [ ] Store `access_token` from response
- [ ] Redirect to dashboard on success

### Login Screen
- [ ] Input field: Phone Number
- [ ] Call `/auth/login/send-otp` on "Send OTP" button
- [ ] Store `otp_session_id` from response
- [ ] Show OTP input screen with timer (10 minutes)
- [ ] Show "Resend OTP" button (after 30 seconds)
- [ ] Call `/auth/login/verify` on "Verify" button
- [ ] Store `access_token` from response
- [ ] Redirect to dashboard on success

### Change Phone Number (During Registration)
- [ ] Show "Change Phone Number" link on OTP screen
- [ ] Input new phone number
- [ ] Call `/auth/update-phone?otp_session_id=X&new_phone=Y`
- [ ] Update `otp_session_id` from response
- [ ] Reset OTP input and timer
- [ ] Show new phone number

### Token Management
- [ ] Store `access_token` in localStorage/sessionStorage
- [ ] Include token in all API requests: `Authorization: Bearer {access_token}`
- [ ] Handle token expiry (redirect to login)

---

## API Base URL
```
Development: http://localhost:8000
Production: https://api.example.com (update with actual URL)
```

---

## Response Format
All responses follow this format:
```json
{
  "response": true/false,
  "title": "Operation Title",
  "data": {...} or null,
  "message": "Success/Info message" or null,
  "error": "Error message" or null
}
```

---

## Common Issues & Solutions

### Issue: "OTP session not found"
- **Cause**: Invalid `otp_session_id`
- **Solution**: Request new OTP

### Issue: "OTP has expired"
- **Cause**: More than 10 minutes have passed
- **Solution**: Click "Resend OTP"

### Issue: "Maximum OTP attempts exceeded"
- **Cause**: More than 5 failed OTP attempts
- **Solution**: Click "Resend OTP" to get a new one

### Issue: "Phone already registered"
- **Cause**: Phone number already has an account
- **Solution**: Use login instead or use different phone

### Issue: "City does not belong to the selected state"
- **Cause**: Selected city is not in the selected state
- **Solution**: Select city from the correct state

---

## Testing Credentials (Development Only)

### Test Phone Numbers
- `+919876543210` (for testing)
- `+919876543211` (for testing)

### Test OTP
- `123456` (works for any session)

### Test State/City
- Get available states from `/states` endpoint
- Get available cities from `/cities?state_id=X` endpoint

---

## Support

For issues or questions:
1. Check the full documentation: `OTP_AUTH_FLOW.md`
2. Review error messages and solutions above
3. Contact backend team

---

## Version History

- **v1.0** (2024-05-27): Initial OTP authentication implementation
  - Registration with OTP
  - Login with OTP
  - Resend OTP
  - Phone number change during registration
  - Development bypass (123456)
