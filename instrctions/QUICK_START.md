# Quick Start Guide - Bot Management

## 🚀 Start the Application

### Terminal 1 - Backend
```powershell
cd 'd:\Research project\PP1 progress\marketmatic\backend'
python app.py
```
✅ Backend running on: http://127.0.0.1:5000

### Terminal 2 - Frontend
```powershell
cd 'd:\Research project\PP1 progress\marketmatic\frontend'
npm run dev
```
✅ Frontend running on: http://localhost:3000

## 🔐 Login as Admin

1. Navigate to: http://localhost:3000/login
2. Use your admin credentials (must have service token)
3. Click **"Chatbot Manager"** card on Admin Dashboard
4. You'll be redirected to: http://localhost:3000/admin/bot-management

## 🤖 Bot Management Interface

### Tab 1: Configuration ⚙️
**What it does:** Configure bot behavior and messages

**How to use:**
1. Write welcome messages in English and Sinhala
2. Set fallback messages (when bot doesn't understand)
3. Toggle RAG/NLP features on/off
4. Set business hours (e.g., 09:00 - 18:00)
5. Click **"Save Configuration"**

### Tab 2: FAQs ❓
**What it does:** Teach bot common questions and answers

**How to use:**
1. Select language (English or Sinhala)
2. Add category (e.g., "Shipping", "Returns")
3. Type question (e.g., "What are your delivery times?")
4. Type answer (e.g., "We deliver Monday-Friday, 9 AM - 6 PM")
5. Click **"Add FAQ"**

**Edit/Delete:**
- Click ✏️ (pencil) to edit
- Click 🗑️ (trash) to delete

### Tab 3: Products 📦
**What it does:** Manage product catalog for bot queries

**How to use:**
1. Fill in product details:
   - Name: "Fresh Apples"
   - Description: "Organic apples from local farms"
   - Category: "Fruits"
   - Price: 450.00 (LKR)
   - Stock: 100
2. Click **"Choose Files"** to upload images
3. Wait for images to upload (shows preview)
4. Click **"Add Product"**

**Note:** Configure Cloudinary first for image uploads!

### Tab 4: Policies 📄
**What it does:** Store company policies for bot reference

**How to use:**
1. Enter policy title: "Return Policy"
2. Select type: General / Return / Shipping / Privacy
3. Write policy content (detailed text)
4. Click **"Add Policy"**

## 📸 Cloudinary Setup (Required for Images)

### Step 1: Create Account
Visit: https://cloudinary.com/users/register_free

### Step 2: Get Credentials
From your dashboard, copy:
- Cloud Name
- API Key
- API Secret

### Step 3: Update .env
Open: `backend/.env`

Replace:
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

With your actual credentials:
```env
CLOUDINARY_CLOUD_NAME=dj4xk3abc
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123
```

### Step 4: Restart Backend
Stop backend (Ctrl+C) and start again:
```powershell
python app.py
```

## 🎯 Quick Tips

### Success Messages ✅
- Green notification = Action successful
- Automatically disappears after 5 seconds

### Error Messages ❌
- Red notification = Something went wrong
- Check console (F12) for details

### Loading States ⏳
- "Loading..." appears when fetching data
- Buttons disabled while processing

### Responsive Design 📱
- Works on mobile, tablet, and desktop
- Sidebar menu on mobile
- Grid layout adjusts automatically

## 🔍 Testing the Bot

### Add Sample Data:

**Configuration:**
```
Welcome (EN): "Welcome to FreshMart! How can I help you today?"
Welcome (SI): "ආයුබෝවන්! මම ඔබට උදව් කරන්නේ කෙසේද?"
Fallback (EN): "I'm sorry, I didn't understand that. Can you rephrase?"
Fallback (SI): "සමාවන්න, මට එය තේරුම් ගත නොහැකි විය. නැවත ප්‍රශ්නය කරන්න?"
```

**Sample FAQ:**
```
Language: English
Category: Shipping
Question: What are your delivery times?
Answer: We deliver Monday to Friday, 9 AM to 6 PM. Orders placed before 2 PM are shipped same day.
```

**Sample Product:**
```
Name: Fresh Apples
Description: Crispy, organic apples from local farms
Category: Fruits
Price: 450.00
Stock: 100
Images: (upload 1-3 images)
```

**Sample Policy:**
```
Title: Return Policy
Type: Return Policy
Content: We accept returns within 7 days of purchase. Items must be in original condition with receipt. Refunds processed within 5-7 business days.
```

## 📊 View Your Data

All data is stored in MongoDB:
- Database: `marketmatic_service`
- Collections:
  - `bot_configurations`
  - `faqs`
  - `products`
  - `policies`

## 🐛 Common Issues

### "Unauthorized" Error
- Check if logged in as admin
- Verify service token exists
- Try logging out and back in

### Images Not Uploading
- Verify Cloudinary credentials in `.env`
- Check internet connection
- Ensure image size < 10MB

### "Failed to load data"
- Check backend is running (http://127.0.0.1:5000)
- Verify MongoDB connection
- Check console for errors

## 📞 Need Help?

1. Check `IMPLEMENTATION_SUMMARY.md` for full documentation
2. Check `BOT_MANAGEMENT_README.md` for API details
3. Check `CLOUDINARY_SETUP.md` for image upload help
4. Check browser console (F12) for error messages

## ✨ You're All Set!

Start managing your chatbot content and watch your AI assistant learn! 🤖
