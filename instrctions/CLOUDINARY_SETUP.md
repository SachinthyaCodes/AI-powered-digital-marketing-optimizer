# Cloudinary Setup Instructions

## Step 1: Sign Up for Cloudinary

1. Go to [https://cloudinary.com/users/register_free](https://cloudinary.com/users/register_free)
2. Create a free account using your email
3. Complete the registration process

## Step 2: Get Your Credentials

1. After logging in, you'll be redirected to your Dashboard
2. On the dashboard, you'll see:
   - **Cloud Name** (e.g., `dj4xk3abc`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123`)

## Step 3: Update .env File

1. Open `backend/.env` file
2. Replace the placeholder values with your actual Cloudinary credentials:

```env
CLOUDINARY_CLOUD_NAME=your-actual-cloud-name
CLOUDINARY_API_KEY=your-actual-api-key
CLOUDINARY_API_SECRET=your-actual-api-secret
```

## Step 4: Test Image Upload

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Log in as an admin and navigate to **Bot Management**
4. Go to the **Products** tab
5. Try uploading a product image to test the integration

## Free Tier Limits

- **Storage**: 25 GB
- **Bandwidth**: 25 GB per month
- **Transformations**: 25,000 per month
- **Images**: Unlimited

## Notes

- Your API Secret is sensitive - never commit it to version control
- The `.env` file is already in `.gitignore` to protect your credentials
- Images are automatically optimized (max 1000x1000px, auto quality)
- All uploaded images are stored in the cloud and accessible via URL
