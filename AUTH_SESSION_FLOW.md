# Auth Session Flow Integration Guide

## Overview

This backend now supports session-based JWT authentication with refresh tokens and device/session tracking for three actor types:

- Admin (`users` table, role = `admin`)
- User (`users` table, role = `user`)
- Vendor (`vendors` table)

## Goals

- Mobile app users stay logged in long-term
- Admin web sessions expire normally
- Vendor web sessions expire normally
- Refresh token rotation is supported
- Blocked/inactive accounts lose API access
- Sessions can be revoked per device/session

---

## Token Model

Every successful login returns:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "access_expires_at": "2026-06-01T10:00:00",
  "refresh_expires_at": "2026-06-15T10:00:00",
  "session_id": 123,
  "user": {}
}
```

### Access Token
Used in:

```http
Authorization: Bearer <access_token>
```

### Refresh Token
Used only for:

```http
POST /api/v1/auth/refresh
```

Backend rotates refresh tokens on every refresh.
Frontend should always replace the old stored refresh token with the new one.

---

## Session Lifetimes

Configured in `backend/.env`:

```env
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_REFRESH_TOKEN_EXPIRE_DAYS=14
VENDOR_ACCESS_TOKEN_EXPIRE_MINUTES=30
VENDOR_REFRESH_TOKEN_EXPIRE_DAYS=14
USER_ACCESS_TOKEN_EXPIRE_MINUTES=43200
USER_REFRESH_TOKEN_EXPIRE_DAYS=3650
```

### Recommended frontend behavior

#### Mobile user
- store both tokens securely
- silently refresh when access token expires
- keep user logged in until:
  - logout
  - app uninstall
  - backend deactivates account
  - session is revoked

#### Admin/Vendor web
- store tokens in secure client storage strategy used by the web app
- refresh access token automatically while refresh token is valid
- force login again when refresh token fails/expired

---

# User Authentication (Mobile App)

## 1. Register flow

### Send OTP
```http
POST /api/v1/auth/register/init
```

### Verify OTP and create session
```http
POST /api/v1/auth/register/verify
```

Request body:

```json
{
  "otp_session_id": 1,
  "otp": "123456",
  "device_id": "device-001",
  "device_name": "Samsung S24",
  "device_platform": "android"
}
```

Response includes access + refresh tokens.

---

## 2. Login flow

### Send OTP
```http
POST /api/v1/auth/login/send-otp
```

### Verify OTP and create mobile session
```http
POST /api/v1/auth/login/verify
```

Request body:

```json
{
  "otp_session_id": 2,
  "otp": "123456",
  "device_id": "device-001",
  "device_name": "Samsung S24",
  "device_platform": "android"
}
```

Response includes long-lived mobile session tokens.

---

# Admin Authentication (Web)

## Login
```http
POST /api/v1/auth/admin/login
```

Request body:

```json
{
  "email": "admin@example.com",
  "password": "secret",
  "device_id": "browser-001",
  "device_name": "Chrome on Mac",
  "device_platform": "web"
}
```

---

# Vendor Authentication (Web)

## Login
```http
POST /api/v1/auth/vendor/login
```

Request body:

```json
{
  "email": "vendor@example.com",
  "password": "secret",
  "device_id": "browser-002",
  "device_name": "Chrome on Windows",
  "device_platform": "web"
}
```

---

# Refresh Session

## Endpoint
```http
POST /api/v1/auth/refresh
```

Request body:

```json
{
  "refresh_token": "<stored_refresh_token>"
}
```

## Response
Returns a fresh pair:

```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "access_expires_at": "...",
  "refresh_expires_at": "...",
  "session_id": 123,
  "user": {}
}
```

## Important rule
Always overwrite:
- old access token
- old refresh token

Because refresh token rotation is enabled.

---

# Logout

## Logout current session
```http
POST /api/v1/auth/logout
```

Requires current access token.

Body may be empty:

```json
{}
```

## Logout all sessions
```http
POST /api/v1/auth/logout-all
```

Requires current access token.

Use this for:
- user security action
- admin self logout everywhere
- vendor self logout everywhere

---

# Account Blocking / Inactive Accounts

If a user or vendor becomes inactive:
- protected APIs stop working
- refresh also fails
- frontend should clear local auth state and redirect to login

Typical backend messages:
- `User not found or inactive`
- `Vendor not found or inactive`
- `Session expired or revoked`
- `Refresh token has expired`
- `Refresh token rotation detected`

---

# Frontend Refresh Strategy

## Suggested approach

1. Make API requests with access token
2. If request fails with 401 because token expired:
   - call `/api/v1/auth/refresh`
3. If refresh succeeds:
   - store new access token
   - store new refresh token
   - retry original request once
4. If refresh fails:
   - clear auth state
   - redirect user to login

---

# Mobile Storage Guidance

## User app
Store securely:
- `access_token`
- `refresh_token`
- `session_id`
- user payload
- optional local `device_id`

Use secure storage depending on platform.

## Web admin/vendor
Use your existing safe web storage strategy and refresh on app load if needed.

---

# Current Auth Endpoints Summary

## Common
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/logout-all`

## User mobile
- `POST /api/v1/auth/register/init`
- `POST /api/v1/auth/register/verify`
- `POST /api/v1/auth/login/send-otp`
- `POST /api/v1/auth/login/verify`
- `POST /api/v1/auth/resend-otp`
- `POST /api/v1/auth/update-phone`

## Admin web
- `POST /api/v1/auth/admin/login`
- `POST /api/v1/auth/admin/bootstrap`

## Vendor web
- `POST /api/v1/auth/vendor/login`

---

# Final Notes

- Admin and user share the `users` table
- Vendors use the `vendors` table
- Session validation is now tied to active session rows
- Refresh token rotation is active
- Mobile users are designed to remain logged in long-term
- Inactive accounts lose access automatically
