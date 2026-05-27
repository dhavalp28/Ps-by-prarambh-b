# Frontend Quick Start - OTP Authentication

## 🚀 5-Minute Setup

### 1. Copy This Code

```javascript
// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// ============ REGISTRATION ============

async function registerStep1() {
  const payload = {
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '+919876543210',
    state_id: 1,
    city_id: 5,
    referral_code: null
  };
  
  const response = await fetch(`${API_BASE_URL}/auth/register/init`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  // data.data.otp_session_id - Save this!
  // data.data.expires_at - Show timer
  return data;
}

async function registerStep2(otpSessionId, otp) {
  const response = await fetch(`${API_BASE_URL}/auth/register/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      otp_session_id: otpSessionId,
      otp: otp
    })
  });
  
  const data = await response.json();
  // data.data.access_token - Save to localStorage!
  // data.data.user - User info
  return data;
}

// ============ LOGIN ============

async function loginStep1(phone) {
  const response = await fetch(`${API_BASE_URL}/auth/login/send-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone: phone })
  });
  
  const data = await response.json();
  // data.data.otp_session_id - Save this!
  return data;
}

async function loginStep2(otpSessionId, otp) {
  const response = await fetch(`${API_BASE_URL}/auth/login/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      otp_session_id: otpSessionId,
      otp: otp
    })
  });
  
  const data = await response.json();
  // data.data.access_token - Save to localStorage!
  return data;
}

// ============ TOKEN MANAGEMENT ============

function saveToken(token) {
  localStorage.setItem('access_token', token);
}

function getToken() {
  return localStorage.getItem('access_token');
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

// ============ AUTHENTICATED REQUESTS ============

async function makeAuthRequest(endpoint, method = 'GET', body = null) {
  const token = getToken();
  
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  };
  
  if (body) options.body = JSON.stringify(body);
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  return await response.json();
}

// ============ HELPER FUNCTIONS ============

async function getStates() {
  const response = await fetch(`${API_BASE_URL}/states`);
  return await response.json();
}

async function getCities(stateId) {
  const response = await fetch(`${API_BASE_URL}/cities?state_id=${stateId}`);
  return await response.json();
}

async function resendOTP(otpSessionId) {
  const response = await fetch(`${API_BASE_URL}/auth/resend-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ otp_session_id: otpSessionId })
  });
  return await response.json();
}

async function updatePhone(otpSessionId, newPhone) {
  const response = await fetch(
    `${API_BASE_URL}/auth/update-phone?otp_session_id=${otpSessionId}&new_phone=${encodeURIComponent(newPhone)}`,
    { method: 'POST', headers: { 'Content-Type': 'application/json' } }
  );
  return await response.json();
}
```

### 2. Registration Flow

```javascript
// Step 1: User fills form and clicks "Send OTP"
const regResult1 = await registerStep1();
if (regResult1.response) {
  const otpSessionId = regResult1.data.otp_session_id;
  // Show OTP input screen
} else {
  alert(regResult1.error);
}

// Step 2: User enters OTP and clicks "Verify"
const regResult2 = await registerStep2(otpSessionId, userEnteredOTP);
if (regResult2.response) {
  saveToken(regResult2.data.access_token);
  // Redirect to dashboard
} else {
  alert(regResult2.error);
}
```

### 3. Login Flow

```javascript
// Step 1: User enters phone and clicks "Send OTP"
const loginResult1 = await loginStep1(userPhone);
if (loginResult1.response) {
  const otpSessionId = loginResult1.data.otp_session_id;
  // Show OTP input screen
} else {
  alert(loginResult1.error);
}

// Step 2: User enters OTP and clicks "Verify"
const loginResult2 = await loginStep2(otpSessionId, userEnteredOTP);
if (loginResult2.response) {
  saveToken(loginResult2.data.access_token);
  // Redirect to dashboard
} else {
  alert(loginResult2.error);
}
```

### 4. Use Token in Requests

```javascript
// Get user profile
const profile = await makeAuthRequest('/users/profile');

// Create business
const business = await makeAuthRequest('/businesses', 'POST', {
  name: 'My Business',
  description: 'Description'
});

// Update user
const updated = await makeAuthRequest('/users/1', 'PUT', {
  first_name: 'Jane'
});
```

---

## 📋 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register/init` | POST | Send registration OTP |
| `/auth/register/verify` | POST | Verify OTP and create user |
| `/auth/login/send-otp` | POST | Send login OTP |
| `/auth/login/verify` | POST | Verify OTP and login |
| `/auth/resend-otp` | POST | Resend OTP |
| `/auth/update-phone` | POST | Update phone during registration |

---

## 🧪 Testing

### Test OTP
Use `123456` as OTP during development.

### Test Phone Numbers
- `+919876543210`
- `+919876543211`

### Test States/Cities
```javascript
const states = await getStates();
const cities = await getCities(1); // state_id = 1
```

---

## ⚠️ Error Handling

```javascript
const errorMessages = {
  'Phone already registered': 'This phone is already registered. Please login.',
  'Email already registered': 'This email is already registered.',
  'OTP has expired': 'OTP expired. Click Resend OTP.',
  'Invalid OTP': 'Incorrect OTP. Please try again.',
  'Maximum OTP attempts exceeded': 'Too many attempts. Click Resend OTP.',
  'User not found': 'Phone not registered. Please register first.',
  'State not found': 'Invalid state selected.',
  'City not found': 'Invalid city selected.'
};

if (!response.response) {
  const message = errorMessages[response.error] || response.error;
  alert(message);
}
```

---

## 💾 Token Storage

```javascript
// Save after login/registration
localStorage.setItem('access_token', token);
localStorage.setItem('user', JSON.stringify(user));

// Get when needed
const token = localStorage.getItem('access_token');
const user = JSON.parse(localStorage.getItem('user'));

// Clear on logout
localStorage.removeItem('access_token');
localStorage.removeItem('user');
```

---

## 🔄 Complete Registration Example

```html
<form id="regForm">
  <input id="firstName" placeholder="First Name" />
  <input id="lastName" placeholder="Last Name" />
  <input id="email" placeholder="Email" />
  <input id="phone" placeholder="Phone" />
  <select id="state"></select>
  <select id="city"></select>
  <button onclick="handleRegister()">Send OTP</button>
</form>

<div id="otpScreen" style="display:none;">
  <input id="otp" placeholder="Enter OTP" maxlength="6" />
  <button onclick="handleVerifyOTP()">Verify</button>
</div>

<script>
let otpSessionId = null;

async function handleRegister() {
  const result = await registerStep1();
  if (result.response) {
    otpSessionId = result.data.otp_session_id;
    document.getElementById('regForm').style.display = 'none';
    document.getElementById('otpScreen').style.display = 'block';
  } else {
    alert(result.error);
  }
}

async function handleVerifyOTP() {
  const otp = document.getElementById('otp').value;
  const result = await registerStep2(otpSessionId, otp);
  if (result.response) {
    saveToken(result.data.access_token);
    window.location.href = '/dashboard';
  } else {
    alert(result.error);
  }
}

// Load states on page load
getStates().then(result => {
  if (result.response) {
    const select = document.getElementById('state');
    result.data.forEach(state => {
      const option = document.createElement('option');
      option.value = state.id;
      option.textContent = state.name;
      select.appendChild(option);
    });
  }
});

// Load cities when state changes
document.getElementById('state').addEventListener('change', async (e) => {
  const result = await getCities(e.target.value);
  if (result.response) {
    const select = document.getElementById('city');
    select.innerHTML = '<option value="">Select City</option>';
    result.data.forEach(city => {
      const option = document.createElement('option');
      option.value = city.id;
      option.textContent = city.name;
      select.appendChild(option);
    });
  }
});
</script>
```

---

## 🔄 Complete Login Example

```html
<form id="loginForm">
  <input id="loginPhone" placeholder="Phone" />
  <button onclick="handleLogin()">Send OTP</button>
</form>

<div id="loginOtpScreen" style="display:none;">
  <input id="loginOtp" placeholder="Enter OTP" maxlength="6" />
  <button onclick="handleLoginVerify()">Verify</button>
</div>

<script>
let loginOtpSessionId = null;

async function handleLogin() {
  const phone = document.getElementById('loginPhone').value;
  const result = await loginStep1(phone);
  if (result.response) {
    loginOtpSessionId = result.data.otp_session_id;
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('loginOtpScreen').style.display = 'block';
  } else {
    alert(result.error);
  }
}

async function handleLoginVerify() {
  const otp = document.getElementById('loginOtp').value;
  const result = await loginStep2(loginOtpSessionId, otp);
  if (result.response) {
    saveToken(result.data.access_token);
    window.location.href = '/dashboard';
  } else {
    alert(result.error);
  }
}
</script>
```

---

## 📱 React Example

```jsx
import { useState } from 'react';

export function RegisterForm() {
  const [step, setStep] = useState(1);
  const [otpSessionId, setOtpSessionId] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    state_id: '',
    city_id: ''
  });
  const [otp, setOtp] = useState('');

  const handleRegisterInit = async () => {
    const result = await registerStep1();
    if (result.response) {
      setOtpSessionId(result.data.otp_session_id);
      setStep(2);
    } else {
      alert(result.error);
    }
  };

  const handleVerifyOTP = async () => {
    const result = await registerStep2(otpSessionId, otp);
    if (result.response) {
      saveToken(result.data.access_token);
      window.location.href = '/dashboard';
    } else {
      alert(result.error);
    }
  };

  return (
    <div>
      {step === 1 ? (
        <form onSubmit={(e) => { e.preventDefault(); handleRegisterInit(); }}>
          <input
            placeholder="First Name"
            value={formData.first_name}
            onChange={(e) => setFormData({...formData, first_name: e.target.value})}
          />
          {/* Other fields */}
          <button type="submit">Send OTP</button>
        </form>
      ) : (
        <div>
          <input
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength="6"
          />
          <button onClick={handleVerifyOTP}>Verify OTP</button>
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 Checklist

- [ ] Copy the code above
- [ ] Update API_BASE_URL to your backend URL
- [ ] Create registration form
- [ ] Create login form
- [ ] Implement token storage
- [ ] Test with OTP: 123456
- [ ] Test error handling
- [ ] Test on mobile
- [ ] Deploy to production

---

## 📞 Need Help?

1. Check FRONTEND_INTEGRATION_GUIDE.md for detailed examples
2. Check OTP_AUTH_QUICK_REFERENCE.md for API details
3. Check error messages and solutions above
4. Contact backend team

---

**Last Updated**: 2024-05-27
**Version**: 1.0
