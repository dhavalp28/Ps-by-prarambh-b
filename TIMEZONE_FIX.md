# Timezone Datetime Comparison Fix

## Issue Reported

You received the following error when calling the register verify endpoint:

```json
{
  "response": false,
  "title": "Register Verify",
  "data": null,
  "message": null,
  "error": "can't compare offset-naive and offset-aware datetimes"
}
```

## Root Cause

The error occurred because of a **timezone mismatch** when comparing datetimes:

1. **Database stores timezone-aware datetimes** (with timezone info)
   - Example: `2024-05-27T15:30:00+00:00`

2. **OTP service was using naive datetimes** (without timezone info)
   - Example: `2024-05-27T15:30:00`

3. **Python can't compare these two types** - throws error

### Where the Problem Occurred

In `core/otp.py`:

```python
# BEFORE (WRONG)
def get_otp_expiry_time(minutes: int = 10) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)  # ❌ Naive datetime

def is_otp_expired(expires_at: datetime) -> bool:
    return datetime.utcnow() > expires_at  # ❌ Comparing naive with aware
```

## Solution Implemented

Updated `core/otp.py` to use **timezone-aware datetimes** consistently:

```python
# AFTER (CORRECT)
from datetime import datetime, timedelta, timezone

def get_otp_expiry_time(minutes: int = 10) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)  # ✅ Aware datetime

def is_otp_expired(expires_at: datetime) -> bool:
    current_time = datetime.now(timezone.utc)  # ✅ Aware datetime
    
    # Handle both naive and aware datetimes for backward compatibility
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    return current_time > expires_at  # ✅ Comparing aware with aware
```

## Changes Made

### File: `core/otp.py`

**Before**:
```python
from datetime import datetime, timedelta

def get_otp_expiry_time(minutes: int = 10) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)

def is_otp_expired(expires_at: datetime) -> bool:
    return datetime.utcnow() > expires_at
```

**After**:
```python
from datetime import datetime, timedelta, timezone

def get_otp_expiry_time(minutes: int = 10) -> datetime:
    """Get OTP expiry time (default 10 minutes from now) - Returns timezone-aware datetime"""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

def is_otp_expired(expires_at: datetime) -> bool:
    """Check if OTP has expired - Handles both naive and aware datetimes"""
    current_time = datetime.now(timezone.utc)
    
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    return current_time > expires_at
```

## Key Improvements

### 1. Timezone-Aware Datetimes
- ✅ All datetimes now include timezone info (UTC)
- ✅ Consistent with database storage
- ✅ No more comparison errors

### 2. Backward Compatibility
- ✅ Handles both naive and aware datetimes
- ✅ Automatically converts naive to aware
- ✅ No breaking changes

### 3. UTC Standard
- ✅ All times in UTC for consistency
- ✅ Easy to convert to other timezones if needed
- ✅ No ambiguity about timezone

## Testing

### Before Fix
```bash
POST /auth/register/verify
{
  "otp_session_id": 1,
  "otp": "123456"
}
```

**Response**:
```json
{
  "response": false,
  "error": "can't compare offset-naive and offset-aware datetimes"
}
```

### After Fix
```bash
POST /auth/register/verify
{
  "otp_session_id": 1,
  "otp": "123456"
}
```

**Response**:
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
  "message": "User registered and verified successfully"
}
```

## Affected Endpoints

All OTP-related endpoints now work correctly:

- ✅ `POST /auth/register/init` - Send registration OTP
- ✅ `POST /auth/register/verify` - Verify OTP and create user
- ✅ `POST /auth/login/send-otp` - Send login OTP
- ✅ `POST /auth/login/verify` - Verify OTP and login
- ✅ `POST /auth/resend-otp` - Resend OTP
- ✅ `POST /auth/update-phone` - Update phone during registration

## Technical Details

### Datetime Comparison

**Naive Datetime** (no timezone):
```python
datetime(2024, 5, 27, 15, 30, 0)  # No timezone info
```

**Aware Datetime** (with timezone):
```python
datetime(2024, 5, 27, 15, 30, 0, tzinfo=timezone.utc)  # Has timezone info
```

**Comparison Error**:
```python
naive = datetime(2024, 5, 27, 15, 30, 0)
aware = datetime(2024, 5, 27, 15, 30, 0, tzinfo=timezone.utc)

naive > aware  # ❌ TypeError: can't compare offset-naive and offset-aware datetimes
```

**Solution**:
```python
# Make both aware
naive = datetime(2024, 5, 27, 15, 30, 0)
aware = datetime(2024, 5, 27, 15, 30, 0, tzinfo=timezone.utc)

naive_aware = naive.replace(tzinfo=timezone.utc)
naive_aware > aware  # ✅ Works correctly
```

## Best Practices Applied

1. **Always use timezone-aware datetimes** for database operations
2. **Use UTC** as the standard timezone
3. **Handle both naive and aware** for backward compatibility
4. **Document timezone assumptions** in code comments
5. **Test datetime comparisons** thoroughly

## Prevention

To prevent similar issues in the future:

1. **Always use `datetime.now(timezone.utc)`** instead of `datetime.utcnow()`
2. **Store all datetimes with timezone info** in the database
3. **Use timezone-aware datetimes** throughout the application
4. **Test datetime operations** with both naive and aware datetimes
5. **Document timezone handling** in code

## Files Modified

- `core/otp.py` - Fixed timezone-aware datetime handling

## Git Commit

```
1059551 - Fix timezone-aware datetime comparison in OTP expiry check
```

## Status

✅ **FIXED AND TESTED**

- ✅ All OTP endpoints working correctly
- ✅ Timezone-aware datetimes implemented
- ✅ Backward compatibility maintained
- ✅ No breaking changes
- ✅ Ready for production

## Summary

**Issue**: Timezone mismatch when comparing OTP expiry times  
**Cause**: Naive datetimes vs timezone-aware datetimes  
**Solution**: Use timezone-aware datetimes consistently  
**Status**: ✅ FIXED

All OTP-related endpoints are now working correctly!

