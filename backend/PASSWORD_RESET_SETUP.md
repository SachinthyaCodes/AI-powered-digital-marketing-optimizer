# Password Reset Setup Guide

## ✅ What's Been Implemented

The forgot password feature is now fully implemented with:

1. ✅ Backend API endpoints for password reset
2. ✅ Email service integration
3. ✅ Secure token-based reset system
4. ✅ Frontend pages (Forgot Password & Reset Password)
5. ✅ Responsive UI design
6. ✅ Token expiration (1 hour)

## 🚀 How to Set It Up (FREE)

### Option 1: Gmail SMTP (Recommended - Easiest & Free)

**Free Limit:** 500 emails/day

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/security
2. Click on "2-Step Verification"
3. Follow the steps to enable it

#### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other" (enter "MarketMatic")
4. Click "Generate"
5. Copy the 16-character password (remove spaces)

#### Step 3: Update Your `.env` File
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
FRONTEND_URL=http://localhost:5173
```

### Option 2: Brevo (formerly Sendinblue)

**Free Limit:** 300 emails/day

1. Sign up at: https://www.brevo.com/
2. Go to SMTP & API settings
3. Generate SMTP key
4. Update `.env`:
```env
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USERNAME=your-brevo-email@example.com
MAIL_PASSWORD=your-brevo-smtp-key
```

### Option 3: Mailgun

**Free Limit:** 5,000 emails/month

1. Sign up at: https://www.mailgun.com/
2. Verify your domain (or use sandbox domain for testing)
3. Get SMTP credentials
4. Update `.env`:
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
```

### Option 4: SendGrid

**Free Limit:** 100 emails/day

1. Sign up at: https://sendgrid.com/
2. Create an API key
3. Update `.env`:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

## 🧪 Testing

### 1. Start Backend
```bash
cd backend
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test the Flow

1. Go to: http://localhost:5173/login
2. Click "Forgot password?"
3. Enter your email
4. Check your email inbox (and spam folder)
5. Click the reset link
6. Enter new password
7. Login with new password

## 📧 Email Template

The password reset email includes:
- ✅ Professional design
- ✅ Secure reset link with token
- ✅ 1-hour expiration notice
- ✅ Security warning if not requested
- ✅ Mobile responsive

## 🔒 Security Features

1. **Token Expiration**: Reset tokens expire after 1 hour
2. **One-Time Use**: Tokens are deleted after successful password reset
3. **Email Enumeration Prevention**: Always returns success message even if email doesn't exist
4. **Secure Tokens**: Uses cryptographically secure random tokens (32 bytes)
5. **Password Hashing**: Passwords are hashed with bcrypt

## 🐛 Troubleshooting

### Email Not Sending?

**Check 1: Environment Variables**
```bash
# In backend directory
cat .env  # Linux/Mac
type .env  # Windows
```

**Check 2: Gmail Issues**
- Make sure 2FA is enabled
- Use App Password, not your regular password
- Check "Less secure app access" is not blocking

**Check 3: Firewall**
- Make sure port 587 is not blocked
- Try port 465 with SSL

**Check 4: Check Logs**
```bash
# Backend console will show email sending errors
```

### Token Invalid/Expired?

- Tokens expire after 1 hour
- Request a new password reset
- Make sure backend time is synchronized

### Still Not Working?

1. Check backend console for errors
2. Check network tab in browser for API errors
3. Verify email credentials are correct
4. Try a different email service

## 📝 API Endpoints

### POST `/api/auth/forgot-password`
Request password reset
```json
{
  "email": "user@example.com"
}
```

### POST `/api/auth/reset-password`
Reset password with token
```json
{
  "token": "reset-token-here",
  "password": "newpassword123"
}
```

### POST `/api/auth/verify-reset-token`
Verify if token is valid
```json
{
  "token": "reset-token-here"
}
```

## 🎉 You're All Set!

The password reset feature is production-ready. Just add your email credentials to the `.env` file and you're good to go!

**Recommended for Production:**
- Use a dedicated email service (Brevo, Mailgun, or SendGrid)
- Don't use personal Gmail for production
- Monitor your email sending limits
- Set up proper error logging
