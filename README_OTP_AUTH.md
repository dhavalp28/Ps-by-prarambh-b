# OTP-Based Authentication System

## 🎯 Overview

A comprehensive OTP (One-Time Password) based authentication system has been implemented for the PS By Prarambh backend. This system eliminates the need for password management and provides a secure, user-friendly authentication flow for both registration and login.

## ✨ Key Features

✅ **OTP-Based Registration** - No passwords required during registration
✅ **OTP-Based Login** - Phone + OTP instead of phone + password
✅ **Phone Verification** - Automatic phone verification during registration
✅ **Resend OTP** - Users can request new OTP if needed
✅ **Phone Number Change** - Users can change phone during registration
✅ **Attempt Limiting** - Maximum 5 failed OTP attempts
✅ **OTP Expiry** - OTPs expire after 10 minutes
✅ **Development Bypass** - "123456" OTP for testing (development only)
✅ **Comprehensive Documentation** - Detailed guides for frontend and backend
✅ **Backward Compatible** - Legacy password-based auth still available

## 📚 Documentation

### For Frontend Developers
- **[OTP_AUTH_QUICK_REFERENCE.md](OTP_AUTH_QUICK_REFERENCE.md)** - Quick reference with API examples
  - Registration and login flow examples
  - API endpoint examples with request/response
  - Error handling guide
  - Frontend implementation checklist
  - Testing credentials

### For Backend Developers
- **[OTP_AUTH_FLOW.md](OTP_AUTH_FLOW.md)** - Comprehensive API documentation
  - Detailed endpoint documentation
  - Request/response schemas
  - Error handling
  - Security considerations
  - Implementation notes

- **[OTP_ARCHITECTURE.md](OTP_ARCHITECTURE.md)** - Architecture and design
  - System architecture diagram
  - Data flow diagrams
  - Database schema
  - State machines
  - Error handling flow
  - Security layers

### For DevOps/Database Administrators
- **[MIGRATION_OTP_AUTH.md](MIGRATION_OTP_AUTH.md)** - Database migration guide
  - Three migration options (Alembic, Manual SQL, Python script)
  - Step-by-step instructions
  - Verification checklist
  - Rollback procedures
  - Troubleshooting guide

### For Project Managers
- **[OTP_IMPLEMENTATION_SUMMARY.md](OTP_IMPLEMENTATION_SUMMARY.md)** - Implementation summary
  - What was implemented
  - File structure
  - Key features
  - Next steps
  - Testing checklist

- **[OTP_IMPLEMENTATION_CHECKLIST.md](OTP_IMPLEMENTATION_CHECKLIST.md)** - Implementation checklist
  - 9 phases with detailed tasks
  - Status tracking
  - Progress monitoring
  - Quick reference

## 🚀 Quick Start

### 1. Database Migration
```bash
# Using Alembic (recommended)
alembic revision --autogenerate -m "Add OTP authentication support"
alembic upgrade head

# Or use manual SQL (see MIGRATION_OTP_AUTH.md)
```

### 2. SMS/Email Integration
- Choose SMS provider (Twilio, AWS SNS, etc.)
- Choose Email provider (SendGrid, AWS SES, etc.)
- Update `services/otp_auth_service.py` with actual implementation
- Configure credentials in `.env`

### 3. Frontend Integration
- Implement registration flow UI
- Implement login flow UI
- Handle OTP session management
- See OTP_AUTH_QUICK_REFERENCE.md for API examples

### 4. Testing
- Test registration flow
- Test login flow
- Test error scenarios
- Test on different devices

### 5. Production Deployment
- Set `is_development = False` in `services/otp_auth_service.py`
- Remove OTP from response
- Configure SMS/Email service
- Deploy to production

## 📋 API Endpoints

### Registration
- `POST /auth/register/init` - Initialize registration, send OTP
- `POST /auth/register/verify` - Verify OTP and create user

### Login
- `POST /auth/login/send-otp` - Send OTP for login
- `POST /auth/login/verify` - Verify OTP and login

### Additional
- `POST /auth/resend-otp` - Resend OTP
- `POST /auth/update-phone` - Update phone during registration

## 🔐 Security Features

1. **OTP Expiry** - OTPs expire after 10 minutes
2. **Attempt Limiting** - Maximum 5 failed attempts per OTP session
3. **Phone Verification** - Users must verify phone during registration
4. **Temporary Data Storage** - User data stored temporarily until OTP verification
5. **Development Bypass** - "123456" bypass for testing (MUST be removed in production)
6. **JWT Tokens** - Secure token-based authentication

## 📁 File Structure

```
backend/
├── db/
│   └── models/
│       ├── user.py (MODIFIED)
│       ├── otp_session.py (NEW)
│       └── init.py (MODIFIED)
├── repositories/
│   └── otp_session_repository.py (NEW)
├── services/
│   ├── auth_service.py (unchanged)
│   └── otp_auth_service.py (NEW)
├── routers/
│   └── routes/
│       └── auth.py (MODIFIED)
├── schemas/
│   └── auth.py (MODIFIED)
├── core/
│   └── otp.py (MODIFIED)
├── OTP_AUTH_FLOW.md
├── OTP_AUTH_QUICK_REFERENCE.md
├── OTP_ARCHITECTURE.md
├── MIGRATION_OTP_AUTH.md
├── OTP_IMPLEMENTATION_SUMMARY.md
├── OTP_IMPLEMENTATION_CHECKLIST.md
└── README_OTP_AUTH.md (this file)
```

## 🧪 Testing

### Development Testing
- Use `123456` as OTP for any session
- Real OTP is returned in response for testing
- Test phone numbers: `+919876543210`, `+919876543211`

### Production Testing
- Use real OTP from SMS/Email
- OTP will NOT be returned in response
- Test with real users

## 🔄 Registration Flow

```
1. User submits registration data
   ↓
2. POST /auth/register/init
   - Validate data
   - Generate OTP
   - Store temporary user data
   ↓
3. User receives OTP
   ↓
4. User enters OTP
   ↓
5. POST /auth/register/verify
   - Verify OTP
   - Create user account
   - Return access token
   ↓
6. User is registered and logged in
```

## 🔄 Login Flow

```
1. User enters phone number
   ↓
2. POST /auth/login/send-otp
   - Generate OTP
   - Send OTP
   ↓
3. User receives OTP
   ↓
4. User enters OTP
   ↓
5. POST /auth/login/verify
   - Verify OTP
   - Return access token
   ↓
6. User is logged in
```

## ⚙️ Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMS Provider (Twilio example)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Email Provider (SendGrid example)
SENDGRID_API_KEY=your-api-key
SENDGRID_FROM_EMAIL=noreply@example.com
```

### Development Mode
```python
# In services/otp_auth_service.py
is_development = True  # Enables "123456" bypass
```

### Production Mode
```python
# In services/otp_auth_service.py
is_development = False  # Disables "123456" bypass
```

## 🐛 Troubleshooting

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

For more troubleshooting, see the relevant documentation files.

## 📊 Implementation Status

| Component | Status | File |
|-----------|--------|------|
| OtpSession Model | ✅ Done | `db/models/otp_session.py` |
| OTP Repository | ✅ Done | `repositories/otp_session_repository.py` |
| OTP Service | ✅ Done | `services/otp_auth_service.py` |
| API Routes | ✅ Done | `routers/routes/auth.py` |
| Schemas | ✅ Done | `schemas/auth.py` |
| OTP Utilities | ✅ Done | `core/otp.py` |
| Documentation | ✅ Done | Multiple `.md` files |
| Database Migration | ⏳ TODO | Run Alembic |
| SMS/Email Integration | ⏳ TODO | Configure provider |
| Frontend Integration | ⏳ TODO | Frontend team |
| Testing | ⏳ TODO | QA team |
| Production Deployment | ⏳ TODO | DevOps team |

## 🎯 Next Steps

1. **Run Database Migration**
   - See MIGRATION_OTP_AUTH.md for detailed instructions

2. **Integrate SMS/Email Service**
   - Choose provider (Twilio, AWS SNS, SendGrid, AWS SES, etc.)
   - Update `services/otp_auth_service.py`
   - Configure credentials in `.env`

3. **Frontend Integration**
   - Implement registration flow UI
   - Implement login flow UI
   - See OTP_AUTH_QUICK_REFERENCE.md for API examples

4. **Testing**
   - Unit tests
   - Integration tests
   - Manual testing
   - Security testing

5. **Production Deployment**
   - Set `is_development = False`
   - Configure production database
   - Configure SMS/Email service
   - Deploy to production

## 📞 Support

For questions or issues:
1. Review the relevant documentation file
2. Check the troubleshooting section
3. Review error messages and solutions
4. Contact the backend team

## 📝 Git Commits

All implementation is committed to GitHub:
- `a736fee` - Implement OTP-based authentication flow
- `a29c737` - Add comprehensive OTP authentication documentation
- `ae92e11` - Add OTP implementation summary document
- `520d6ac` - Add OTP authentication architecture documentation
- `16df5a5` - Add OTP implementation checklist

## 🎉 Summary

The OTP-based authentication system is fully implemented and ready for:
1. Database migration
2. SMS/Email integration
3. Frontend integration
4. Testing and deployment

All code is committed to GitHub and comprehensively documented.

---

**Last Updated**: 2024-05-27
**Version**: 1.0
**Status**: Backend Implementation Complete ✅
