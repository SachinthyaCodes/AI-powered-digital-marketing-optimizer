# MarketMatic Backend

Python Flask backend for MarketMatic - SME Chatbot Service

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env` file

5. Run the server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/me` - Get current user info

### Health Check
- `GET /` - API info
- `GET /api/health` - Health check
