# MarketMatic - SME Chatbot Service

A modern web application for Small and Medium Enterprises (SMEs) featuring an AI-powered chatbot service.

## Project Structure

```
marketmatic/
├── backend/                 # Python Flask Backend
│   ├── auth/               # Authentication handlers
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── database.py         # Database connection
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
└── frontend/               # React Frontend
    ├── src/
    │   ├── components/     # Reusable components
    │   ├── context/        # React contexts
    │   ├── pages/          # Page components
    │   ├── services/       # API services
    │   ├── App.jsx         # Main app component
    │   └── main.jsx        # Entry point
    ├── package.json        # Node dependencies
    └── .env                # Environment variables
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Update the `.env` file with your MongoDB credentials (already configured)

6. Run the backend server:
```bash
python app.py
```

The backend will start at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start at `http://localhost:3000`

## Features

### Backend Features
- ✅ User Authentication (JWT-based)
- ✅ MongoDB Integration
- ✅ Secure Password Hashing (bcrypt)
- ✅ Email Validation
- ✅ CORS Configuration
- ✅ RESTful API Design

### Frontend Features
- ✅ Modern React 18 with Vite
- ✅ Responsive Design with Tailwind CSS
- ✅ User Authentication Flow
- ✅ Protected Routes
- ✅ Context API for State Management
- ✅ Beautiful UI with Lucide Icons
- ✅ Form Validation
- ✅ Loading States & Error Handling

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/me` - Get current user info

### Health Check
- `GET /` - API info
- `GET /api/health` - Health check

## Technologies Used

### Backend
- Python 3.x
- Flask (Web Framework)
- MongoDB (Database)
- PyMongo (MongoDB Driver)
- JWT (Authentication)
- bcrypt (Password Hashing)

### Frontend
- React 18
- Vite (Build Tool)
- React Router (Routing)
- Axios (HTTP Client)
- Tailwind CSS (Styling)
- Lucide React (Icons)

## Environment Variables

### Backend (.env)
```
MONGODB_URL=mongodb+srv://sanuda:sanuda@cluster0.gkdrjfi.mongodb.net/
DATABASE_NAME=marketmatic_service
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000
```

## Default Credentials

Create a new account using the signup page. The application uses secure password hashing, so all passwords are encrypted in the database.

## Development

- Backend runs on port 5000
- Frontend runs on port 3000
- Both servers need to be running simultaneously for full functionality

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Protected API routes
- CORS configuration
- Email validation
- Secure password requirements (minimum 6 characters)

## Contributing

This is a research project for PP1 progress.

## License

Private - Research Project
