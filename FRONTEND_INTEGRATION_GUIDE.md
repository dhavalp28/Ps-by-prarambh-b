# Frontend Integration Guide - OTP Authentication

## Overview

This guide provides step-by-step instructions for frontend developers to integrate the OTP-based authentication system into their application.

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

## Part 1: Registration Flow

### Step 1: Registration Form

Create a registration form with the following fields:

```html
<form id="registrationForm">
  <input type="text" id="firstName" placeholder="First Name" required />
  <input type="text" id="lastName" placeholder="Last Name" required />
  <input type="email" id="email" placeholder="Email" required />
  <input type="tel" id="phone" placeholder="Phone (+919876543210)" required />
  
  <select id="state" required>
    <option value="">Select State</option>
    <!-- Populate from /states endpoint -->
  </select>
  
  <select id="city" required>
    <option value="">Select City</option>
    <!-- Populate from /cities?state_id=X endpoint -->
  </select>
  
  <input type="text" id="referralCode" placeholder="Referral Code (Optional)" />
  
  <button type="button" onclick="sendRegistrationOTP()">Send OTP</button>
</form>
```

### Step 2: Load States and Cities

```javascript
// Load states on page load
async function loadStates() {
  try {
    const response = await fetch('http://localhost:8000/states');
    const data = await response.json();
    
    if (data.response) {
      const stateSelect = document.getElementById('state');
      data.data.forEach(state => {
        const option = document.createElement('option');
        option.value = state.id;
        option.textContent = state.name;
        stateSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading states:', error);
  }
}

// Load cities when state changes
document.getElementById('state').addEventListener('change', async (e) => {
  const stateId = e.target.value;
  if (!stateId) return;
  
  try {
    const response = await fetch(`http://localhost:8000/cities?state_id=${stateId}`);
    const data = await response.json();
    
    if (data.response) {
      const citySelect = document.getElementById('city');
      citySelect.innerHTML = '<option value="">Select City</option>';
      data.data.forEach(city => {
        const option = document.createElement('option');
        option.value = city.id;
        option.textContent = city.name;
        citySelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading cities:', error);
  }
});

// Call on page load
loadStates();
```

### Step 3: Send Registration OTP

```javascript
let otpSessionId = null;
let otpExpiryTime = null;

async function sendRegistrationOTP() {
  const firstName = document.getElementById('firstName').value;
  const lastName = document.getElementById('lastName').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;
  const stateId = parseInt(document.getElementById('state').value);
  const cityId = parseInt(document.getElementById('city').value);
  const referralCode = document.getElementById('referralCode').value || null;
  
  // Validation
  if (!firstName || !lastName || !email || !phone || !stateId || !cityId) {
    alert('Please fill all required fields');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/auth/register/init', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone,
        state_id: stateId,
        city_id: cityId,
        referral_code: referralCode
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      // Success
      otpSessionId = data.data.otp_session_id;
      otpExpiryTime = new Date(data.data.expires_at);
      
      alert('OTP sent successfully!');
      showOTPVerificationScreen();
      startOTPTimer();
    } else {
      // Error
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to send OTP');
  }
}
```

### Step 4: OTP Verification Screen

```html
<div id="otpVerificationScreen" style="display: none;">
  <h2>Verify OTP</h2>
  <p>OTP sent to: <span id="displayPhone"></span></p>
  
  <input type="text" id="otpInput" placeholder="Enter 6-digit OTP" maxlength="6" />
  
  <p>Time remaining: <span id="otpTimer">10:00</span></p>
  
  <button type="button" onclick="verifyRegistrationOTP()">Verify OTP</button>
  <button type="button" onclick="resendOTP()">Resend OTP</button>
  <button type="button" onclick="changePhoneNumber()">Change Phone Number</button>
</div>
```

### Step 5: Verify Registration OTP

```javascript
async function verifyRegistrationOTP() {
  const otp = document.getElementById('otpInput').value;
  
  if (!otp || otp.length !== 6) {
    alert('Please enter a valid 6-digit OTP');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/auth/register/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        otp_session_id: otpSessionId,
        otp: otp
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      // Success - User registered and logged in
      const accessToken = data.data.access_token;
      const user = data.data.user;
      
      // Store token
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      alert('Registration successful!');
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      // Error
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to verify OTP');
  }
}
```

### Step 6: Resend OTP

```javascript
async function resendOTP() {
  try {
    const response = await fetch('http://localhost:8000/auth/resend-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        otp_session_id: otpSessionId
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      otpExpiryTime = new Date(data.data.expires_at);
      document.getElementById('otpInput').value = '';
      alert('New OTP sent successfully!');
      startOTPTimer();
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to resend OTP');
  }
}
```

### Step 7: Change Phone Number

```javascript
async function changePhoneNumber() {
  const newPhone = prompt('Enter new phone number:');
  if (!newPhone) return;
  
  try {
    const response = await fetch(
      `http://localhost:8000/auth/update-phone?otp_session_id=${otpSessionId}&new_phone=${encodeURIComponent(newPhone)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    const data = await response.json();
    
    if (data.response) {
      otpExpiryTime = new Date(data.data.expires_at);
      document.getElementById('otpInput').value = '';
      document.getElementById('displayPhone').textContent = data.data.phone;
      alert('OTP sent to new phone number!');
      startOTPTimer();
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to update phone number');
  }
}
```

### Step 8: OTP Timer

```javascript
let timerInterval = null;

function startOTPTimer() {
  if (timerInterval) clearInterval(timerInterval);
  
  timerInterval = setInterval(() => {
    const now = new Date();
    const diff = otpExpiryTime - now;
    
    if (diff <= 0) {
      clearInterval(timerInterval);
      document.getElementById('otpTimer').textContent = 'Expired';
      alert('OTP has expired. Please request a new one.');
      return;
    }
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    document.getElementById('otpTimer').textContent = 
      `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, 1000);
}

function showOTPVerificationScreen() {
  document.getElementById('registrationForm').style.display = 'none';
  document.getElementById('otpVerificationScreen').style.display = 'block';
  document.getElementById('displayPhone').textContent = document.getElementById('phone').value;
}
```

---

## Part 2: Login Flow

### Step 1: Login Form

```html
<form id="loginForm">
  <input type="tel" id="loginPhone" placeholder="Phone (+919876543210)" required />
  <button type="button" onclick="sendLoginOTP()">Send OTP</button>
</form>
```

### Step 2: Send Login OTP

```javascript
let loginOtpSessionId = null;
let loginOtpExpiryTime = null;

async function sendLoginOTP() {
  const phone = document.getElementById('loginPhone').value;
  
  if (!phone) {
    alert('Please enter your phone number');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/auth/login/send-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone: phone
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      loginOtpSessionId = data.data.otp_session_id;
      loginOtpExpiryTime = new Date(data.data.expires_at);
      
      alert('OTP sent successfully!');
      showLoginOTPVerificationScreen();
      startLoginOTPTimer();
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to send OTP');
  }
}
```

### Step 3: Login OTP Verification Screen

```html
<div id="loginOtpVerificationScreen" style="display: none;">
  <h2>Verify OTP</h2>
  <p>OTP sent to: <span id="loginDisplayPhone"></span></p>
  
  <input type="text" id="loginOtpInput" placeholder="Enter 6-digit OTP" maxlength="6" />
  
  <p>Time remaining: <span id="loginOtpTimer">10:00</span></p>
  
  <button type="button" onclick="verifyLoginOTP()">Verify OTP</button>
  <button type="button" onclick="resendLoginOTP()">Resend OTP</button>
  <button type="button" onclick="backToLoginForm()">Back</button>
</div>
```

### Step 4: Verify Login OTP

```javascript
async function verifyLoginOTP() {
  const otp = document.getElementById('loginOtpInput').value;
  
  if (!otp || otp.length !== 6) {
    alert('Please enter a valid 6-digit OTP');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/auth/login/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        otp_session_id: loginOtpSessionId,
        otp: otp
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      // Success - User logged in
      const accessToken = data.data.access_token;
      const user = data.data.user;
      
      // Store token
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      alert('Login successful!');
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to verify OTP');
  }
}
```

### Step 5: Resend Login OTP

```javascript
async function resendLoginOTP() {
  try {
    const response = await fetch('http://localhost:8000/auth/resend-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        otp_session_id: loginOtpSessionId
      })
    });
    
    const data = await response.json();
    
    if (data.response) {
      loginOtpExpiryTime = new Date(data.data.expires_at);
      document.getElementById('loginOtpInput').value = '';
      alert('New OTP sent successfully!');
      startLoginOTPTimer();
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to resend OTP');
  }
}
```

### Step 6: Login OTP Timer

```javascript
let loginTimerInterval = null;

function startLoginOTPTimer() {
  if (loginTimerInterval) clearInterval(loginTimerInterval);
  
  loginTimerInterval = setInterval(() => {
    const now = new Date();
    const diff = loginOtpExpiryTime - now;
    
    if (diff <= 0) {
      clearInterval(loginTimerInterval);
      document.getElementById('loginOtpTimer').textContent = 'Expired';
      alert('OTP has expired. Please request a new one.');
      return;
    }
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    document.getElementById('loginOtpTimer').textContent = 
      `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, 1000);
}

function showLoginOTPVerificationScreen() {
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('loginOtpVerificationScreen').style.display = 'block';
  document.getElementById('loginDisplayPhone').textContent = document.getElementById('loginPhone').value;
}

function backToLoginForm() {
  if (loginTimerInterval) clearInterval(loginTimerInterval);
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('loginOtpVerificationScreen').style.display = 'none';
  document.getElementById('loginOtpInput').value = '';
}
```

---

## Part 3: Token Management

### Store Token

```javascript
// After successful login/registration
localStorage.setItem('access_token', accessToken);
localStorage.setItem('user', JSON.stringify(user));
```

### Get Token

```javascript
function getAccessToken() {
  return localStorage.getItem('access_token');
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}
```

### Use Token in API Requests

```javascript
async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
  const token = getAccessToken();
  
  if (!token) {
    // Redirect to login
    window.location.href = '/login';
    return;
  }
  
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    // Check if token expired (401 Unauthorized)
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return;
    }
    
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

### Logout

```javascript
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

---

## Part 4: Error Handling

### Common Errors and Solutions

```javascript
function handleAuthError(error) {
  const errorMessages = {
    'Phone already registered': 'This phone is already registered. Please login instead.',
    'Email already registered': 'This email is already registered. Please use a different email.',
    'OTP has expired': 'OTP expired. Click "Resend OTP" to get a new one.',
    'Invalid OTP': 'Incorrect OTP. Please try again.',
    'Maximum OTP attempts exceeded': 'Too many failed attempts. Click "Resend OTP" to try again.',
    'User not found': 'Phone number not registered. Please register first.',
    'State not found': 'Selected state is invalid. Please select a valid state.',
    'City not found': 'Selected city is invalid. Please select a valid city.',
    'City does not belong to the selected state': 'Selected city does not belong to the selected state.'
  };
  
  return errorMessages[error] || error;
}

// Usage
if (!data.response) {
  const userFriendlyError = handleAuthError(data.error);
  alert(userFriendlyError);
}
```

---

## Part 5: Complete Example (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
  <title>OTP Authentication</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; }
    form { display: flex; flex-direction: column; gap: 10px; }
    input, select, button { padding: 10px; font-size: 16px; }
    button { background-color: #007bff; color: white; border: none; cursor: pointer; }
    button:hover { background-color: #0056b3; }
    .hidden { display: none; }
  </style>
</head>
<body>
  <h1>Authentication</h1>
  
  <!-- Registration Form -->
  <div id="registrationSection">
    <h2>Register</h2>
    <form id="registrationForm">
      <input type="text" id="firstName" placeholder="First Name" required />
      <input type="text" id="lastName" placeholder="Last Name" required />
      <input type="email" id="email" placeholder="Email" required />
      <input type="tel" id="phone" placeholder="Phone" required />
      <select id="state" required>
        <option value="">Select State</option>
      </select>
      <select id="city" required>
        <option value="">Select City</option>
      </select>
      <input type="text" id="referralCode" placeholder="Referral Code (Optional)" />
      <button type="button" onclick="sendRegistrationOTP()">Send OTP</button>
    </form>
  </div>
  
  <!-- Registration OTP Verification -->
  <div id="otpVerificationScreen" class="hidden">
    <h2>Verify OTP</h2>
    <p>OTP sent to: <span id="displayPhone"></span></p>
    <input type="text" id="otpInput" placeholder="Enter 6-digit OTP" maxlength="6" />
    <p>Time remaining: <span id="otpTimer">10:00</span></p>
    <button type="button" onclick="verifyRegistrationOTP()">Verify OTP</button>
    <button type="button" onclick="resendOTP()">Resend OTP</button>
    <button type="button" onclick="changePhoneNumber()">Change Phone</button>
  </div>
  
  <!-- Login Form -->
  <div id="loginSection">
    <h2>Login</h2>
    <form id="loginForm">
      <input type="tel" id="loginPhone" placeholder="Phone" required />
      <button type="button" onclick="sendLoginOTP()">Send OTP</button>
    </form>
  </div>
  
  <!-- Login OTP Verification -->
  <div id="loginOtpVerificationScreen" class="hidden">
    <h2>Verify OTP</h2>
    <p>OTP sent to: <span id="loginDisplayPhone"></span></p>
    <input type="text" id="loginOtpInput" placeholder="Enter 6-digit OTP" maxlength="6" />
    <p>Time remaining: <span id="loginOtpTimer">10:00</span></p>
    <button type="button" onclick="verifyLoginOTP()">Verify OTP</button>
    <button type="button" onclick="resendLoginOTP()">Resend OTP</button>
    <button type="button" onclick="backToLoginForm()">Back</button>
  </div>
  
  <script>
    // Include all JavaScript code from above sections here
  </script>
</body>
</html>
```

---

## Testing Checklist

- [ ] Registration form loads with states
- [ ] Cities populate when state is selected
- [ ] OTP is sent on "Send OTP" button click
- [ ] OTP verification screen appears
- [ ] OTP timer counts down correctly
- [ ] OTP verification works with correct OTP
- [ ] Error messages display correctly
- [ ] Resend OTP works
- [ ] Change phone number works
- [ ] Login form works
- [ ] Login OTP verification works
- [ ] Token is stored in localStorage
- [ ] User is redirected to dashboard after login
- [ ] Logout clears token and redirects to login

---

## API Response Examples

### Successful Registration Init
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

### Successful Registration Verify
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

### Error Response
```json
{
  "response": false,
  "title": "Register Init",
  "data": null,
  "message": null,
  "error": "Phone already registered"
}
```

---

## Development Testing

### Test OTP
Use `123456` as OTP for any session during development.

### Test Phone Numbers
- `+919876543210`
- `+919876543211`

### Test States/Cities
Get available states from `/states` endpoint and cities from `/cities?state_id=X` endpoint.

---

## Production Checklist

- [ ] Remove development OTP bypass (123456)
- [ ] Configure SMS/Email service
- [ ] Update API base URL to production
- [ ] Test with real OTPs
- [ ] Test error handling
- [ ] Test token expiry
- [ ] Test on different devices/browsers
- [ ] Test network error handling
- [ ] Implement proper logging
- [ ] Add analytics tracking

---

## Support

For issues or questions:
1. Check the error messages and solutions above
2. Review the API documentation
3. Check browser console for errors
4. Contact backend team
