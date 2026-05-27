# OTP Authentication Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Application                         │
│  (Web/Mobile - Registration & Login UI)                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      FastAPI Backend                                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Routes (auth.py)                      │  │
│  │                                                              │  │
│  │  POST /auth/register/init      ─────────────────────────┐   │  │
│  │  POST /auth/register/verify    ─────────────────────────┤   │  │
│  │  POST /auth/login/send-otp     ─────────────────────────┤   │  │
│  │  POST /auth/login/verify       ─────────────────────────┤   │  │
│  │  POST /auth/resend-otp         ─────────────────────────┤   │  │
│  │  POST /auth/update-phone       ─────────────────────────┤   │  │
│  │                                                          │   │  │
│  └──────────────────────────────────────────────────────────┼───┘  │
│                                                             │       │
│  ┌──────────────────────────────────────────────────────────▼───┐  │
│  │              OTP Auth Service (otp_auth_service.py)         │  │
│  │                                                              │  │
│  │  • register_init()                                          │  │
│  │  • register_verify()                                        │  │
│  │  • login_send_otp()                                         │  │
│  │  • login_verify()                                           │  │
│  │  • resend_otp()                                             │  │
│  │  • update_phone_during_registration()                       │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                    │                    │                 │
│         │                    │                    │                 │
│  ┌──────▼──────┐  ┌──────────▼────────┐  ┌──────▼──────────┐      │
│  │ OTP Session │  │ User Repository   │  │ OTP Utilities   │      │
│  │ Repository  │  │                   │  │                 │      │
│  │             │  │ • get_user_by_*   │  │ • generate_otp()│      │
│  │ • create    │  │ • create_user()   │  │ • verify_otp()  │      │
│  │ • get       │  │ • update_user()   │  │ • is_expired()  │      │
│  │ • update    │  │                   │  │                 │      │
│  │ • delete    │  └───────────────────┘  └─────────────────┘      │
│  │ • increment │                                                   │
│  │   attempts  │                                                   │
│  └──────┬──────┘                                                   │
│         │                                                          │
└─────────┼──────────────────────────────────────────────────────────┘
          │
          │ SQLAlchemy ORM
          │
┌─────────▼──────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    otp_sessions Table                        │ │
│  │                                                              │ │
│  │  id (PK)  │ phone │ otp │ purpose │ temp_user_data │ ...   │ │
│  │  ─────────┼───────┼─────┼─────────┼────────────────┼─────  │ │
│  │  1        │ +91.. │ 654 │ register│ {user_data}    │ ...   │ │
│  │  2        │ +91.. │ 321 │ login   │ NULL           │ ...   │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                      users Table                             │ │
│  │                                                              │ │
│  │  id │ first_name │ email │ phone │ is_phone_verified │ ... │ │
│  │  ───┼────────────┼───────┼───────┼───────────────────┼──── │ │
│  │  1  │ John       │ j@... │ +91.. │ true              │ ... │ │
│  │  2  │ Jane       │ j@... │ +91.. │ false             │ ... │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Registration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Initialize Registration
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ Collect: first_name, last_name, email, phone, state, city   │
│ └─ POST /auth/register/init                                     │
│                                                                  │
│ Backend (register_init)                                         │
│ ├─ Validate phone not registered                               │
│ ├─ Validate email not registered                               │
│ ├─ Validate state exists                                       │
│ ├─ Validate city exists and belongs to state                   │
│ ├─ Generate OTP (6 digits)                                     │
│ ├─ Create OtpSession with temp_user_data                       │
│ ├─ TODO: Send OTP via SMS/Email                                │
│ └─ Return: otp_session_id, phone, expires_at                   │
│                                                                  │
│ Database                                                        │
│ └─ INSERT INTO otp_sessions (phone, otp, purpose, ...)         │
└──────────────────────────────────────────────────────────────────┘

Step 2: User Receives OTP
┌──────────────────────────────────────────────────────────────────┐
│ SMS/Email Service                                               │
│ └─ Send OTP to user's phone/email                               │
└──────────────────────────────────────────────────────────────────┘

Step 3: Verify OTP
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ User enters OTP                                              │
│ └─ POST /auth/register/verify                                   │
│                                                                  │
│ Backend (register_verify)                                       │
│ ├─ Get OtpSession by ID                                        │
│ ├─ Check if OTP expired (> 10 minutes)                         │
│ ├─ Check attempts (< 5)                                        │
│ ├─ Increment attempts                                          │
│ ├─ Verify OTP (entered_otp == real_otp OR "123456")           │
│ ├─ Parse temp_user_data                                        │
│ ├─ Create User with is_phone_verified = true                   │
│ ├─ Mark OtpSession as verified                                 │
│ ├─ Generate JWT access token                                   │
│ └─ Return: access_token, token_type, user                      │
│                                                                  │
│ Database                                                        │
│ ├─ INSERT INTO users (first_name, last_name, ...)             │
│ └─ UPDATE otp_sessions SET is_verified = true                  │
└──────────────────────────────────────────────────────────────────┘

Step 4: User Logged In
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ Store access_token                                           │
│ ├─ Store user info                                              │
│ └─ Redirect to dashboard                                        │
└──────────────────────────────────────────────────────────────────┘
```

### Login Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LOGIN FLOW                                     │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Send OTP
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ User enters phone number                                     │
│ └─ POST /auth/login/send-otp                                    │
│                                                                  │
│ Backend (login_send_otp)                                        │
│ ├─ Get user by phone                                           │
│ ├─ Check if user exists                                        │
│ ├─ Check if phone is verified                                  │
│ ├─ Generate OTP (6 digits)                                     │
│ ├─ Create OtpSession with purpose="login"                      │
│ ├─ TODO: Send OTP via SMS/Email                                │
│ └─ Return: otp_session_id, phone, expires_at                   │
│                                                                  │
│ Database                                                        │
│ ├─ SELECT * FROM users WHERE phone = ?                         │
│ └─ INSERT INTO otp_sessions (phone, otp, purpose, ...)         │
└──────────────────────────────────────────────────────────────────┘

Step 2: User Receives OTP
┌──────────────────────────────────────────────────────────────────┐
│ SMS/Email Service                                               │
│ └─ Send OTP to user's phone/email                               │
└──────────────────────────────────────────────────────────────────┘

Step 3: Verify OTP
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ User enters OTP                                              │
│ └─ POST /auth/login/verify                                      │
│                                                                  │
│ Backend (login_verify)                                          │
│ ├─ Get OtpSession by ID                                        │
│ ├─ Check if OTP expired (> 10 minutes)                         │
│ ├─ Check attempts (< 5)                                        │
│ ├─ Increment attempts                                          │
│ ├─ Verify OTP (entered_otp == real_otp OR "123456")           │
│ ├─ Get user by phone                                           │
│ ├─ Mark OtpSession as verified                                 │
│ ├─ Generate JWT access token                                   │
│ └─ Return: access_token, token_type, user                      │
│                                                                  │
│ Database                                                        │
│ ├─ SELECT * FROM users WHERE phone = ?                         │
│ └─ UPDATE otp_sessions SET is_verified = true                  │
└──────────────────────────────────────────────────────────────────┘

Step 4: User Logged In
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ Store access_token                                           │
│ ├─ Store user info                                              │
│ └─ Redirect to dashboard                                        │
└──────────────────────────────────────────────────────────────────┘
```

### Phone Number Change During Registration

```
┌─────────────────────────────────────────────────────────────────────┐
│            PHONE NUMBER CHANGE DURING REGISTRATION                  │
└─────────────────────────────────────────────────────────────────────┘

Step 1: User Changes Phone
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ User clicks "Change Phone Number"                            │
│ ├─ User enters new phone number                                 │
│ └─ POST /auth/update-phone?otp_session_id=X&new_phone=Y        │
│                                                                  │
│ Backend (update_phone_during_registration)                      │
│ ├─ Get OtpSession by ID                                        │
│ ├─ Check if already verified                                   │
│ ├─ Validate new phone not registered                           │
│ ├─ Update phone in OtpSession                                  │
│ ├─ Generate new OTP                                            │
│ ├─ Reset attempts to 0                                         │
│ ├─ TODO: Send new OTP to new phone                             │
│ └─ Return: otp_session_id, new_phone, expires_at               │
│                                                                  │
│ Database                                                        │
│ └─ UPDATE otp_sessions SET phone=?, otp=?, attempts=0          │
└──────────────────────────────────────────────────────────────────┘

Step 2: User Receives OTP on New Phone
┌──────────────────────────────────────────────────────────────────┐
│ SMS/Email Service                                               │
│ └─ Send new OTP to new phone number                             │
└──────────────────────────────────────────────────────────────────┘

Step 3: Verify OTP with New Phone
┌──────────────────────────────────────────────────────────────────┐
│ Frontend                                                         │
│ ├─ User enters OTP from new phone                               │
│ └─ POST /auth/register/verify                                   │
│                                                                  │
│ Backend (register_verify)                                       │
│ ├─ Verify OTP                                                  │
│ ├─ Create user with new phone number                           │
│ ├─ Mark phone as verified                                      │
│ └─ Return: access_token, user                                  │
│                                                                  │
│ Database                                                        │
│ ├─ INSERT INTO users (phone=new_phone, ...)                    │
│ └─ UPDATE otp_sessions SET is_verified = true                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### OtpSession Table

```sql
CREATE TABLE otp_sessions (
    id SERIAL PRIMARY KEY,
    phone VARCHAR NOT NULL,
    otp VARCHAR NOT NULL,
    purpose VARCHAR NOT NULL,  -- 'register' or 'login'
    temp_user_data VARCHAR,     -- JSON string with user data
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_otp_sessions_phone ON otp_sessions(phone);
```

### Users Table (Updated)

```sql
ALTER TABLE users ADD COLUMN is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;
```

---

## State Machine Diagrams

### OTP Session States

```
┌─────────────────────────────────────────────────────────────────┐
│                    OTP SESSION STATES                           │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   CREATED        │
                    │ (OTP Generated)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼────────┐
                    │  PENDING        │
                    │ (Awaiting OTP)  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
         ┌──────▼──────┐ ┌──▼────────┐ ┌─▼──────────┐
         │  EXPIRED    │ │ VERIFIED  │ │ MAX_FAILED │
         │ (> 10 min)  │ │ (OTP OK)  │ │ (5 attempts)
         └─────────────┘ └──┬────────┘ └────────────┘
                            │
                    ┌───────▼────────┐
                    │  COMPLETED     │
                    │ (User Created) │
                    └────────────────┘
```

### User Registration States

```
┌─────────────────────────────────────────────────────────────────┐
│                  USER REGISTRATION STATES                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  NOT_REGISTERED  │
└────────┬─────────┘
         │
         │ POST /auth/register/init
         │
┌────────▼──────────────────┐
│  AWAITING_OTP_VERIFICATION │
│ (Temp data stored)         │
└────────┬───────────────────┘
         │
         │ POST /auth/register/verify (OTP correct)
         │
┌────────▼──────────────────┐
│  REGISTERED                │
│ (User created)             │
│ (is_phone_verified = true) │
└────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   ERROR HANDLING FLOW                           │
└─────────────────────────────────────────────────────────────────┘

API Request
    │
    ├─ Validation Error?
    │  └─ Return 400 Bad Request
    │
    ├─ Resource Not Found?
    │  └─ Return 404 Not Found
    │
    ├─ Business Logic Error?
    │  ├─ Phone already registered? → 400
    │  ├─ Email already registered? → 400
    │  ├─ State not found? → 404
    │  ├─ City not found? → 404
    │  ├─ OTP expired? → 400
    │  ├─ Invalid OTP? → 400
    │  ├─ Max attempts exceeded? → 400
    │  └─ User not found? → 404
    │
    ├─ Server Error?
    │  └─ Return 500 Internal Server Error
    │
    └─ Success?
       └─ Return 200 OK with data
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                               │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Input Validation
├─ Phone format validation
├─ Email format validation
├─ OTP format validation (6 digits)
└─ Required field validation

Layer 2: Business Logic Validation
├─ Phone uniqueness check
├─ Email uniqueness check
├─ State/City existence check
└─ Phone verification requirement

Layer 3: OTP Security
├─ OTP expiry (10 minutes)
├─ Attempt limiting (5 attempts)
├─ Random OTP generation
└─ Development bypass (123456 - dev only)

Layer 4: Authentication
├─ JWT token generation
├─ Token expiry (configurable)
└─ Token validation on protected routes

Layer 5: Database Security
├─ Parameterized queries (SQLAlchemy ORM)
├─ Password hashing (bcrypt)
└─ Temporary data cleanup
```

---

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│              PERFORMANCE OPTIMIZATION                           │
└─────────────────────────────────────────────────────────────────┘

Database Indexes:
├─ otp_sessions.phone (for fast OTP session lookup)
├─ users.phone (for fast user lookup)
└─ users.email (for fast email lookup)

Query Optimization:
├─ Use indexed columns in WHERE clauses
├─ Avoid N+1 queries
└─ Use connection pooling

Caching Opportunities:
├─ Cache state/city lists
├─ Cache user data after login
└─ Cache OTP session data

Scalability:
├─ Stateless API design
├─ Horizontal scaling ready
└─ Database connection pooling
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEPLOYMENT ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

Development Environment:
├─ Local PostgreSQL
├─ Development bypass enabled (123456)
├─ OTP returned in response
└─ SMS/Email not sent

Staging Environment:
├─ Staging PostgreSQL
├─ Development bypass enabled (123456)
├─ OTP returned in response
└─ SMS/Email integration tested

Production Environment:
├─ Production PostgreSQL
├─ Development bypass disabled
├─ OTP NOT returned in response
└─ SMS/Email integration active
```

---

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                  INTEGRATION POINTS                             │
└─────────────────────────────────────────────────────────────────┘

Frontend Integration:
├─ Registration flow UI
├─ Login flow UI
├─ OTP input screen
├─ Phone change screen
└─ Token management

SMS/Email Integration:
├─ Twilio (SMS)
├─ AWS SNS (SMS)
├─ SendGrid (Email)
├─ AWS SES (Email)
└─ Custom SMS provider

Database Integration:
├─ PostgreSQL
├─ Alembic migrations
└─ SQLAlchemy ORM

Authentication Integration:
├─ JWT tokens
├─ Protected routes
├─ Token refresh (future)
└─ Role-based access (future)
```

---

## Monitoring & Logging

```
┌─────────────────────────────────────────────────────────────────┐
│              MONITORING & LOGGING POINTS                        │
└─────────────────────────────────────────────────────────────────┘

API Endpoints:
├─ Request/response logging
├─ Error logging
├─ Performance metrics
└─ User activity tracking

OTP Operations:
├─ OTP generation logging
├─ OTP verification attempts
├─ OTP expiry tracking
└─ Failed attempt tracking

Database Operations:
├─ Query logging
├─ Connection pool monitoring
├─ Transaction logging
└─ Error logging

Security Events:
├─ Failed login attempts
├─ Max attempts exceeded
├─ Suspicious activity
└─ Token validation failures
```

---

This architecture provides a scalable, secure, and maintainable OTP-based authentication system.
