# Bot Management System - MarketMatic

## Overview

The Bot Management system allows admins to configure and manage their AI-powered chatbot with support for:
- **RAG (Retrieval Augmented Generation)** - Knowledge base powered by FAQs, products, and policies
- **NLP (Natural Language Processing)** - Intent recognition and natural language understanding
- **Multilingual Support** - English and Sinhala languages
- **Product Catalog** - Manage products with images, prices, and stock
- **FAQ Management** - Add questions and answers in multiple languages
- **Policy Management** - Store return, shipping, privacy, and general policies

## Features

### 1. Bot Configuration
- Set welcome messages (English & Sinhala)
- Configure fallback messages for unrecognized queries
- Enable/disable RAG and NLP features
- Set business hours
- Configure offline messages

### 2. FAQ Management
- Add, edit, and delete FAQs
- Multilingual support (English/Sinhala)
- Categorize FAQs (e.g., Shipping, Products, Returns)
- Search and filter capabilities

### 3. Product Management
- Add products with details:
  - Name, description, category
  - Price (LKR)
  - Stock quantity
  - Multiple product images
- Image upload via Cloudinary (automatic optimization)
- Edit and delete products
- Track inventory levels

### 4. Policy Management
- Store company policies:
  - Return Policy
  - Shipping Policy
  - Privacy Policy
  - General Policies
- Rich text content support
- Easy editing and updates

## API Endpoints

### Configuration
- `GET /api/bot/config` - Get bot configuration
- `PUT /api/bot/config` - Update bot configuration

### FAQs
- `GET /api/bot/faqs` - List all FAQs
- `POST /api/bot/faqs` - Add new FAQ
- `PUT /api/bot/faqs/:id` - Update FAQ
- `DELETE /api/bot/faqs/:id` - Delete FAQ

### Products
- `GET /api/bot/products` - List all products
- `POST /api/bot/products` - Add new product
- `PUT /api/bot/products/:id` - Update product
- `DELETE /api/bot/products/:id` - Delete product
- `POST /api/bot/products/:id/images` - Upload product images

### Policies
- `GET /api/bot/policies` - List all policies
- `POST /api/bot/policies` - Add new policy
- `PUT /api/bot/policies/:id` - Update policy
- `DELETE /api/bot/policies/:id` - Delete policy

### Image Upload
- `POST /api/bot/upload-image` - Upload general images

## Authentication

All bot management endpoints require admin authentication:
- Admin must have a valid service token
- JWT token must be included in Authorization header
- Only admins can access bot management features

## Database Collections

### bot_configurations
```javascript
{
  service_id: ObjectId,
  welcome_message: { en: String, si: String },
  fallback_message: { en: String, si: String },
  language_support: [String],
  rag_enabled: Boolean,
  nlp_enabled: Boolean,
  business_hours: { start: String, end: String },
  offline_message: { en: String, si: String },
  created_at: Date,
  updated_at: Date
}
```

### faqs
```javascript
{
  service_id: ObjectId,
  question: String,
  answer: String,
  language: String,
  category: String,
  created_at: Date,
  updated_at: Date
}
```

### products
```javascript
{
  service_id: ObjectId,
  name: String,
  description: String,
  price: Number,
  stock: Number,
  category: String,
  images: [String],
  created_at: Date,
  updated_at: Date
}
```

### policies
```javascript
{
  service_id: ObjectId,
  title: String,
  content: String,
  policy_type: String,
  created_at: Date,
  updated_at: Date
}
```

## Image Storage

Images are stored on Cloudinary with:
- Automatic optimization (max 1000x1000px)
- Auto quality adjustment
- CDN delivery for fast loading
- Secure URLs
- Image transformation support

## Usage

### Admin Access
1. Log in as an admin with a valid service token
2. Navigate to Admin Dashboard
3. Click "Chatbot Manager" card
4. Access the Bot Management interface

### Adding FAQs
1. Go to "FAQs" tab
2. Select language (English/Sinhala)
3. Add category (optional)
4. Enter question and answer
5. Click "Add FAQ"

### Adding Products
1. Go to "Products" tab
2. Fill in product details
3. Upload product images (multiple supported)
4. Set price and stock quantity
5. Click "Add Product"

### Managing Policies
1. Go to "Policies" tab
2. Enter policy title
3. Select policy type
4. Write policy content
5. Click "Add Policy"

## Future Enhancements

- [ ] Voice message support
- [ ] Analytics dashboard for bot interactions
- [ ] A/B testing for responses
- [ ] Sentiment analysis
- [ ] Integration with WhatsApp Business API
- [ ] Facebook Messenger integration
- [ ] Real-time chat monitoring
- [ ] Customer feedback collection
- [ ] Automated response suggestions
- [ ] Multi-agent support

## Technical Stack

**Backend:**
- Flask 3.0.0
- PyMongo 4.6.0
- Cloudinary 1.44.1
- Pillow 12.0.0

**Frontend:**
- React 18
- Tailwind CSS
- Lucide React Icons
- React Router v6

**Database:**
- MongoDB Atlas

**Image Storage:**
- Cloudinary (Free tier: 25GB storage, 25GB bandwidth/month)
