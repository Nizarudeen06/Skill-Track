# ✅ VERIFIED WORKING CREDENTIALS

**Status**: Tested and working via API  
**Backend**: http://localhost:8000 ✅  
**Frontend**: http://localhost:5173 ✅  

---

## 🔑 TESTED LOGIN CREDENTIALS

### ✅ ADMINISTRATOR (Verified Working)
```
Email: admin@college.edu
Password: Password@123
```

**Test Result**: ✅ Successfully authenticated via API
```json
{
  "id": 1,
  "name": "Ms. Anitha",
  "email": "admin@college.edu",
  "role": "admin",
  "is_active": true
}
```

**Direct API Login Test**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@college.edu","password":"Password@123"}'
```

---

## 🌐 HOW TO LOGIN

### Method 1: Via Frontend (Recommended)
1. Open: http://localhost:5173
2. Click "Login" button
3. Enter:
   - **Email**: `admin@college.edu`
   - **Password**: `Password@123`
4. Click "Sign In"

### Method 2: Direct API Test
```bash
# Test login directly
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@college.edu","password":"Password@123"}'

# Should return JWT token and user object
```

---

## 👥 ALL AVAILABLE ACCOUNTS

### Password for ALL accounts: `Password@123`

| Role | Email | Access Level |
|------|-------|--------------|
| 👨‍💼 Admin | `admin@college.edu` | Full system access |
| 🏢 Owner | `owner@college.edu` | Domain management |
| 👁️ Invigilator | `invigilator@college.edu` | Issue exam keys |

---

## ⚙️ TROUBLESHOOTING

### If Login Still Doesn't Work:

#### 1. Check Backend is Running
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","environment":"development","version":"2.1.0"}
```

#### 2. Check Frontend is Running
```bash
curl http://localhost:5173
# Should return HTML with "SkillTrack"
```

#### 3. Clear Browser Cache
- Press `Ctrl + Shift + Delete`
- Clear all cookies and cache
- Refresh page

#### 4. Check Browser Console
- Press `F12` to open DevTools
- Go to Console tab
- Look for any red errors
- Common issues:
  - CORS errors (backend issue)
  - Network errors (connection issue)
  - 401 errors (wrong credentials)

#### 5. Verify Password Exactly
The password is case-sensitive:
- ✅ Correct: `Password@123`
- ❌ Wrong: `password@123`
- ❌ Wrong: `PASSWORD@123`
- ❌ Wrong: `Password@12`

---

## 🧪 VERIFY SERVERS ARE WORKING

### Backend Health Check
```bash
# Basic health
curl http://localhost:8000/health

# Detailed health with database status
curl http://localhost:8000/health/detailed
```

Expected Response:
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "environment": "development",
  "checks": {
    "database": {"status": "healthy"},
    "scheduler": {"status": "healthy"}
  }
}
```

### Test Login via API
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@college.edu","password":"Password@123"}'
```

If this works but frontend login doesn't:
- Clear browser cache
- Check browser console for errors
- Try incognito/private browsing mode

---

## 🔄 RESTART SERVERS

If you need to restart:

### Stop All Servers
```bash
# Find and kill backend
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill

# Find and kill frontend
ps aux | grep node | grep vite | awk '{print $2}' | xargs kill
```

### Start Backend
```bash
cd skilltrack-api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
cd skilltrack
npm run dev
```

---

## 📝 PASSWORD REQUIREMENTS

The password `Password@123` meets all security requirements:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter (P)
- ✅ At least one lowercase letter (assword)
- ✅ At least one digit (1, 2, 3)
- ✅ At least one special character (@)

---

## 🎯 QUICK ACCESS

**Frontend Application**: http://localhost:5173  
**Backend API**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs  
**API Alternative Docs**: http://localhost:8000/redoc  

---

## 📞 STILL HAVING ISSUES?

### Check Backend Logs
```bash
cd skilltrack-api
tail -f backend.log
```

### Check Frontend Console
1. Open http://localhost:5173
2. Press F12 (DevTools)
3. Go to Console tab
4. Look for errors

### Common Error Messages:

**"Invalid email or password"**
- Double-check password is exactly: `Password@123`
- Verify email is: `admin@college.edu`

**"Network Error"**
- Backend not running
- Check: `curl http://localhost:8000/health`

**"CORS Error"**
- Frontend .env file missing or wrong
- Should have: `VITE_API_URL=http://localhost:8000`

**"Too many failed attempts"**
- Wait 60 seconds (rate limiting)
- Or restart backend to reset

---

## ✅ CONFIRMATION

These credentials have been **VERIFIED WORKING** via direct API call:

```bash
$ curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@college.edu","password":"Password@123"}'

Response:
{
  "access_token": "eyJhbGc...[valid JWT token]",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Ms. Anitha",
    "email": "admin@college.edu",
    "role": "admin",
    "is_active": true
  }
}
```

**Status**: ✅ **CREDENTIALS WORKING**

---

*Last Verified: October 8, 2026*  
*Backend Status: ✅ Running*  
*Frontend Status: ✅ Running*  
*Database Status: ✅ Seeded with demo data*
