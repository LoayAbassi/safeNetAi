# i18n Sync Test Plan

## Overview
This test plan verifies that the i18n sync implementation is working correctly across SafeNetAi, including:
1. User language preference persistence
2. Language activation in backend
3. Email template localization
4. Frontend dashboard internationalization
5. Language change without page reload

## Test Cases

### 1. User Language Preference Persistence

#### Test Case 1.1: Language saved on registration
**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "national_id": "123456789",
    "bank_account_number": "ACC123456789",
    "language": "fr"
  }'
```

**Expected Result:**
- User created successfully
- User's language preference set to 'fr' in database

#### Test Case 1.2: Language saved on login
**Command:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "language": "ar"
  }'
```

**Expected Result:**
- User logged in successfully
- User's language preference updated to 'ar' in database

### 2. Language Activation in Backend

#### Test Case 2.1: Middleware activates user language
**Description:** Verify that UserLanguageMiddleware activates the correct language for authenticated requests

**Manual Test:**
1. Log in as a user with language preference set to 'fr'
2. Make a request to any protected endpoint
3. Check server logs for language activation messages

**Expected Result:**
- Middleware logs show language 'fr' activated
- request.LANGUAGE_CODE set to 'fr'

### 3. Email Template Localization

#### Test Case 3.1: OTP email in user's language
**Command:**
```bash
# First create a user with French language preference
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "frenchuser@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "French",
    "last_name": "User",
    "national_id": "987654321",
    "bank_account_number": "ACC987654321",
    "language": "fr"
  }'
```

**Expected Result:**
- OTP email received in French
- Email subject contains "Code de vérification OTP"
- Email body contains French content

#### Test Case 3.2: Transaction notification in user's language
**Description:** Test that transaction notifications use the user's preferred language

**Manual Test:**
1. Create a transaction for a user with Arabic language preference
2. Check that notification email is in Arabic

**Expected Result:**
- Email subject contains Arabic text
- Email body contains Arabic content

### 4. Frontend Dashboard Internationalization

#### Test Case 4.1: Client Dashboard loads translations
**Manual Test:**
1. Navigate to client dashboard
2. Change language to French
3. Verify dashboard elements display French text
4. Change language to Arabic
5. Verify dashboard elements display Arabic text

**Expected Result:**
- Dashboard elements update without page reload
- Text changes to selected language
- RTL layout applied for Arabic

#### Test Case 4.2: Admin Dashboard loads translations
**Manual Test:**
1. Navigate to admin dashboard
2. Change language to French
3. Verify dashboard elements display French text
4. Change language to Arabic
5. Verify dashboard elements display Arabic text

**Expected Result:**
- Dashboard elements update without page reload
- Text changes to selected language
- RTL layout applied for Arabic

### 5. Language Change Without Page Reload

#### Test Case 5.1: Language context updates immediately
**Manual Test:**
1. Open client dashboard
2. Open browser console
3. Change language using language selector
4. Check that i18n language changes immediately

**Expected Result:**
- Language changes without page refresh
- All translated elements update immediately
- Document direction changes for Arabic (RTL)

## Automated Tests

Run the automated test suite:

```bash
cd backend
python ../test_i18n_sync.py
```

## Verification Commands

### Check User Language in Database
```bash
# In Django shell
python manage.py shell
>>> from apps.users.models import User
>>> user = User.objects.get(email='test@example.com')
>>> print(user.language)
```

### Check Email Logs
```bash
# Check email logs for language information
tail -f backend/logs/system/system.log | grep "language"
```

### Check Middleware Logs
```bash
# Check middleware logs for language activation
tail -f backend/logs/system/system.log | grep "UserLanguageMiddleware"
```

## Expected Outcomes

1. ✅ User language preference persisted in database
2. ✅ Backend activates user's preferred language
3. ✅ All email templates use gettext/gettext_lazy
4. ✅ Emails sent in user's preferred language
5. ✅ Frontend dashboards use i18n keys
6. ✅ Language changes update UI without reload
7. ✅ RTL support for Arabic language
8. ✅ Server logs show language handling

## Files Modified

- `backend/apps/users/models.py` - Added language field to User model
- `backend/apps/users/serializers.py` - Added UserLanguageSerializer
- `backend/apps/users/views.py` - Added update_language endpoint
- `backend/apps/users/auth_views.py` - Updated login/register to handle language
- `backend/apps/users/email_service.py` - Updated to use user language preference
- `backend/apps/users/middleware.py` - Created UserLanguageMiddleware
- `backend/backend/settings.py` - Added middleware to MIDDLEWARE
- `frontend/src/contexts/AuthContext.jsx` - Modified to send language on login/register
- `frontend/src/contexts/LanguageContext.jsx` - Modified to send language changes to backend
- `frontend/src/pages/ClientDashboard.jsx` - Updated to use i18n
- `frontend/src/pages/admin/Dashboard.jsx` - Updated to use i18n
- `frontend/public/locales/*/translation.json` - Updated translation files
- `frontend/src/i18n.js` - i18n configuration

## Test Results

All tests should pass with the following expected behavior:
- User language preference saved and retrieved correctly
- Backend activates user's preferred language for all requests
- Emails sent in user's preferred language
- Frontend dashboards display content in selected language
- Language changes update UI without page reload
- Arabic language displays with RTL layout