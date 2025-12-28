# Deployment Guide

## Production Deployment Checklist

### Before Deployment

- [ ] All models trained and saved in `SavedModels/`
- [ ] Environment variables configured
- [ ] MongoDB database created
- [ ] API keys secured
- [ ] Code tested locally
- [ ] Dependencies documented

## Backend Deployment

### Option 1: Heroku

1. **Install Heroku CLI:**
```bash
heroku login
```

2. **Create Heroku app:**
```bash
cd backend
heroku create your-app-name
```

3. **Add buildpack:**
```bash
heroku buildpacks:set heroku/python
```

4. **Set environment variables:**
```bash
heroku config:set STORAGE_TOKEN=your_gemini_api_key
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set DB_NAME=marketing_optimizer
```

5. **Create Procfile:**
```
web: gunicorn app:app
```

6. **Update requirements.txt:**
Add `gunicorn` to requirements.txt

7. **Deploy:**
```bash
git push heroku main
```

### Option 2: AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04)

2. **Connect and install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Clone repository:**
```bash
git clone your-repo-url
cd backend
```

4. **Setup virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. **Configure environment:**
```bash
nano .env
# Add your environment variables
```

6. **Create systemd service** (`/etc/systemd/system/marketing-api.service`):
```ini
[Unit]
Description=Marketing Optimizer API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
Environment="PATH=/home/ubuntu/backend/venv/bin"
ExecStart=/home/ubuntu/backend/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

7. **Start service:**
```bash
sudo systemctl start marketing-api
sudo systemctl enable marketing-api
```

8. **Configure Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 3: Google Cloud Run

1. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

2. **Build and deploy:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/marketing-api
gcloud run deploy marketing-api --image gcr.io/YOUR_PROJECT_ID/marketing-api --platform managed
```

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Deploy:**
```bash
cd frontend
vercel
```

3. **Configure environment:**
- Add backend URL in Vercel dashboard
- Update `API_BASE_URL` in App.js to production URL

### Option 2: Netlify

1. **Install Netlify CLI:**
```bash
npm install -g netlify-cli
```

2. **Build:**
```bash
cd frontend
npm run build
```

3. **Deploy:**
```bash
netlify deploy --prod --dir=build
```

4. **Configure redirects** (create `public/_redirects`):
```
/api/* https://your-backend-url.com/api/:splat 200
/* /index.html 200
```

### Option 3: AWS S3 + CloudFront

1. **Build:**
```bash
cd frontend
npm run build
```

2. **Create S3 bucket:**
```bash
aws s3 mb s3://your-bucket-name
```

3. **Upload files:**
```bash
aws s3 sync build/ s3://your-bucket-name
```

4. **Configure bucket for static hosting:**
```bash
aws s3 website s3://your-bucket-name --index-document index.html
```

5. **Create CloudFront distribution** for HTTPS and caching

## Database Setup

### MongoDB Atlas (Production)

1. **Create cluster** on MongoDB Atlas

2. **Whitelist IP addresses:**
   - Add your server IPs
   - Or use 0.0.0.0/0 (not recommended for production)

3. **Create database user:**
   - Username and password
   - Grant read/write permissions

4. **Get connection string:**
```
mongodb+srv://username:password@cluster.mongodb.net/
```

## Environment Variables

### Backend (.env)
```env
# Production settings
STORAGE_TOKEN=your_actual_gemini_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=marketing_optimizer_prod
FLASK_ENV=production
FLASK_DEBUG=False
```

### Frontend
Update `API_BASE_URL` in `App.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.com/api';
```

## Security Considerations

### Backend
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Enable CORS only for specific origins
- [ ] Implement rate limiting
- [ ] Add authentication/API keys
- [ ] Sanitize user inputs
- [ ] Use environment variables for secrets
- [ ] Enable request logging
- [ ] Set up monitoring

### Frontend
- [ ] Use environment variables
- [ ] Implement CSP headers
- [ ] Sanitize user inputs
- [ ] Use HTTPS
- [ ] Implement error boundaries

## Post-Deployment

### Monitoring

1. **Backend monitoring:**
   - Use services like New Relic, Datadog
   - Monitor API response times
   - Track error rates

2. **Frontend monitoring:**
   - Google Analytics
   - Sentry for error tracking

### Backup

1. **Database backups:**
   - Enable MongoDB Atlas automated backups
   - Or use mongodump regularly

2. **Model backups:**
   - Store models in S3/Google Cloud Storage
   - Version control

### CI/CD Pipeline

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
          appdir: "backend"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID}}
          vercel-project-id: ${{ secrets.PROJECT_ID}}
          working-directory: ./frontend
```

## Performance Optimization

### Backend
- Use Redis for caching frequent predictions
- Implement request queuing for high load
- Use CDN for model files
- Optimize model loading (lazy loading)

### Frontend
- Enable code splitting
- Optimize images
- Use lazy loading
- Enable service workers
- Minify and compress assets

## Testing in Production

1. **Smoke tests:**
```bash
curl https://your-backend-url.com/health
```

2. **Load testing:**
```bash
# Install Apache Bench
ab -n 1000 -c 10 https://your-backend-url.com/api/predict
```

3. **Monitor logs:**
```bash
heroku logs --tail  # For Heroku
# Or check CloudWatch for AWS
```

## Rollback Plan

1. Keep previous version deployed
2. Use blue-green deployment
3. Have database backup ready
4. Document rollback steps

## Cost Estimation

### Heroku (Backend)
- Hobby: $7/month
- Standard: $25-50/month

### Vercel (Frontend)
- Free tier available
- Pro: $20/month

### MongoDB Atlas
- Free tier: 512MB
- M10: $57/month

### Total Estimated Cost
- Development: $0-10/month
- Production: $50-150/month

## Support Contacts

- Heroku Support: https://help.heroku.com
- Vercel Support: https://vercel.com/support
- MongoDB Support: https://support.mongodb.com

---

**Note:** Replace all placeholder values (your-app-name, your-domain.com, etc.) with actual values before deployment.
