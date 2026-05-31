# Redemption QR Flow Frontend Integration Guide

## Purpose

This document explains the correct frontend integration for coupon redemption.

## Important Rule

Coupon redemption is allowed **only after successful QR verification**.

The scanned QR must belong to the **same business** whose coupon the user selected.

That means the frontend flow is:

1. user opens Business Details page
2. user sees active coupons of that business
3. user selects a coupon and taps `Redeem`
4. app opens QR scanner
5. app scans the QR shown by that business
6. QR provides the business code
7. frontend sends `business_id + coupon_id + scanned business code` to backend
8. backend validates QR/business/coupon/subscription rules
9. backend creates redemption history and returns success

---

## Base URLs

API routes:

```text
/api/v1
```

App business routes:

```text
/app
```

Example local:

```text
http://localhost:8000/api/v1
http://localhost:8000/app
```

---

## Auth Header

Authenticated requests must send:

```http
Authorization: Bearer <access_token>
```

---

## Standard Response Wrapper

Success:

```json
{
  "response": true,
  "title": "Coupon Claimed",
  "data": {},
  "message": "Created successfully",
  "error": null
}
```

Error:

```json
{
  "response": false,
  "title": "Coupon Claim",
  "data": null,
  "message": null,
  "error": "Scanned QR code does not belong to the selected business"
}
```

If frontend uses the existing Axios interceptor in `frontend/lib/api.ts`, successful responses are already unwrapped to `response.data.data`.

---

# Step 1: Load Business Details

## Endpoint

```http
GET /app/businesses/details/{business_id}
```

## Purpose

Use this on the business details page.

## Coupon fields available in response

```json
{
  "coupons": [
    {
      "id": 12,
      "coupon_name": "Flat 20% Off",
      "discount": 20,
      "description": "Valid on dine-in",
      "valid_till": "2026-06-30",
      "validity_days": null,
      "max_redemption_count": 100,
      "redemption_count": 5,
      "remaining_redemptions": 95,
      "is_active": true,
      "status": "Active",
      "not_valid_on": ["Sunday"],
      "is_expired": false,
      "can_redeem": true,
      "effective_expiry_date": "2026-06-30",
      "created_at": "2026-05-31T10:00:00",
      "updated_at": "2026-05-31T10:00:00"
    }
  ]
}
```

## Frontend use

- render all active coupons for the business
- keep selected `business_id`
- when user taps `Redeem`, save selected `coupon_id`
- then open QR scanner

---

# Step 2: Scan Business QR

## Expected QR content

The QR already generated in admin contains the business code / business identifier used by backend.

Frontend developer should:
- scan QR
- extract business code from QR payload
- send that scanned code to backend

## Frontend rule

Do **not** redeem directly from coupon selection alone.

Redemption request must happen only **after scan success**.

---

# Step 3: Claim Coupon After QR Verification

## Endpoint

```http
POST /api/v1/redemptions/claim
```

## Auth

Required.

## Request body

```json
{
  "business_id": 5,
  "coupon_id": 12,
  "code": "ABC123"
}
```

Where:
- `business_id` = business page currently open
- `coupon_id` = coupon selected by user
- `code` = business code scanned from QR

---

## Backend validations performed

Backend validates all of the following:

- user has active subscription
- subscription is not expired
- scanned business code exists and is valid
- scanned QR business matches the selected `business_id`
- coupon exists
- coupon is active
- coupon belongs to the selected business
- coupon is not expired
- current day is not present in `coupon.not_valid_on`
- coupon max redemption count is not exceeded
- user subscription daily limit is not exceeded
- user subscription total limit is not exceeded

---

## Success response

```json
{
  "response": true,
  "title": "Coupon Claimed",
  "data": {
    "success": true,
    "message": "Coupon redeemed successfully",
    "redemption_id": 44,
    "claim_reference": 12,
    "coupon_id": 12,
    "business_id": 5,
    "business_name": "Cafe Mocha",
    "remaining_daily_limit": 2,
    "remaining_total_limit": 18,
    "daily_redemption_count": 1,
    "total_redemption_count": 7,
    "coupon": {
      "id": 12,
      "coupon_name": "Flat 20% Off",
      "discount": 20.0,
      "is_active": true
    }
  },
  "message": "Created successfully",
  "error": null
}
```

## Important note

`claim_reference` is not a generated claim code.

It is exactly:

```text
claim_reference = coupon_id
```

So if coupon id is `12`, claim reference is also `12`.

---

## Frontend actions on success

After success:

- close scanner
- show success UI
- show `claim_reference`
- refresh business details if you want updated coupon count
- refresh redemption summary if shown
- refresh redemption history if shown

---

# Optional QR Code Validation Endpoint

If frontend wants to validate scanned code before final claim, this endpoint exists.

## Endpoint

```http
POST /api/v1/redemptions/validate-code
```

## Request body

```json
{
  "code": "ABC123"
}
```

## Example success response

```json
{
  "response": true,
  "title": "Business Code Validation",
  "data": {
    "valid": true,
    "business_id": 5,
    "business_name": "Cafe Mocha",
    "message": "Business code is valid"
  }
}
```

## Suggested usage

Optional pattern:

1. scan QR
2. call `validate-code`
3. verify returned `business_id === selected business_id`
4. then call `POST /redemptions/claim`

This is optional because the final claim endpoint already performs the same safety validation.

---

# Redemption Summary Endpoint

## Endpoint

```http
GET /api/v1/redemptions/summary
```

## Example response

```json
{
  "response": true,
  "title": "Redemption Summary",
  "data": {
    "total_redeemed_today": 1,
    "total_redeemed_all_time": 7,
    "remaining_daily_limit": 2,
    "remaining_total_limit": 18,
    "subscription_expires_at": "2026-06-30T23:59:59",
    "is_subscription_active": true,
    "daily_redemption_count": 1,
    "total_redemption_count": 7,
    "last_redeemed_on": "2026-05-31"
  }
}
```

Use this to show remaining coupon usage to the user.

---

# Redemption History Endpoint

## Endpoint

```http
GET /api/v1/redemptions/history?skip=0&limit=10
```

## Example item

```json
{
  "id": 44,
  "user_id": 9,
  "business_id": 5,
  "business_code_id": 3,
  "user_subscription_id": 11,
  "coupon_id": 12,
  "claim_reference": 12,
  "status": "success",
  "remaining_daily_limit": 2,
  "remaining_total_limit": 18,
  "redeemed_at": "2026-05-31T10:30:00",
  "created_at": "2026-05-31T10:30:00",
  "business": {
    "id": 5,
    "business_name": "Cafe Mocha"
  },
  "coupon": {
    "id": 12,
    "coupon_name": "Flat 20% Off",
    "discount": 20.0,
    "is_active": true
  }
}
```

Every successful coupon redemption creates one history record.
This is the audit log for admin reporting and tracking.

---

# Error Messages Frontend Should Handle

Common errors:

- `No active subscription found`
- `Subscription is inactive`
- `Subscription has expired`
- `Coupon not found`
- `Coupon does not belong to this business`
- `Coupon is inactive`
- `Coupon has expired`
- `Coupon is not valid on Sunday`
- `Coupon redemption limit reached`
- `Daily redemption limit exceeded`
- `Total redemption limit exceeded`
- `Business code not found`
- `Scanned QR code does not belong to the selected business`

---

# Recommended Frontend Sequence

## Business details flow

1. call `GET /app/businesses/details/{business_id}`
2. render business coupons
3. user taps `Redeem`
4. open QR scanner
5. scan business QR
6. extract business code from QR
7. call `POST /api/v1/redemptions/claim`
8. show success using returned `claim_reference`

---

# Minimal Frontend Example

```ts
const claimCouponAfterQrScan = async (
  businessId: number,
  couponId: number,
  scannedCode: string,
) => {
  const response = await api.post("/redemptions/claim", {
    business_id: businessId,
    coupon_id: couponId,
    code: scannedCode,
  });

  return response.data;
};
```

Expected unwrapped success payload with current Axios interceptor:

```ts
{
  success: true,
  message: "Coupon redeemed successfully",
  redemption_id: 44,
  claim_reference: 12,
  coupon_id: 12,
  business_id: 5,
  business_name: "Cafe Mocha",
  remaining_daily_limit: 2,
  remaining_total_limit: 18,
  daily_redemption_count: 1,
  total_redemption_count: 7,
  coupon: {
    id: 12,
    coupon_name: "Flat 20% Off",
    discount: 20,
    is_active: true,
  },
}
```

---

# Source References

- `backend/routers/routes/redemption.py`
- `backend/services/redemption_service.py`
- `backend/schemas/redemption_history.py`
- `backend/routers/routes/app_business.py`
- `backend/services/business_service.py`

---

# Final Notes

- Redemption must happen only after QR scan
- scanned QR business must match selected business
- the only supported app redemption endpoint is `POST /api/v1/redemptions/claim`
- `claim_reference` always equals `coupon_id`
- every successful redemption creates a redemption history record
