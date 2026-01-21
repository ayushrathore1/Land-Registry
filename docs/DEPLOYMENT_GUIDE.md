# Deployment Guide

## Land Record Digitization Tool

This guide covers deploying the application in development and production environments.

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.9 or higher |
| RAM | 2 GB minimum |
| Storage | 500 MB for application + data |
| Browser | Chrome 90+, Firefox 88+, Edge 90+ |

### Recommended

| Component | Recommendation |
|-----------|----------------|
| Python | 3.11+ |
| RAM | 4 GB or more |
| Storage | SSD recommended |
| Network | 10 Mbps+ connection |

---

## Project Structure

```
Land Records/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── pyproject.toml       # Python dependencies
│   ├── routes/              # API route handlers
│   └── services/            # Business logic
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── styles.css           # Stylesheets
│   └── js/                  # JavaScript modules
├── data/
│   ├── spatial/             # GeoJSON parcels
│   └── textual/             # CSV land records
└── docs/                    # Documentation
```

---

## Development Setup

### Step 1: Clone/Download the Project

```bash
cd "x:\Land Records"
```

### Step 2: Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -e .
```

Or install directly:

```bash
pip install fastapi uvicorn python-jose passlib bcrypt rapidfuzz pandas pydantic python-multipart
```

### Step 4: Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Step 5: Serve the Frontend

**Using Python's built-in server:**

```bash
cd frontend
python -m http.server 3000
```

**Using VS Code Live Server:**

1. Install Live Server extension
2. Right-click `index.html`
3. Select "Open with Live Server"

The frontend will be available at: `http://localhost:3000`

### Step 6: Verify Installation

1. Open `http://localhost:3000` in browser
2. Map should load with colored parcels
3. Search should return results
4. Check browser console for errors

---

## Production Deployment

### Option A: Single Server Deployment

#### 1. Install Production Dependencies

```bash
pip install gunicorn
```

#### 2. Create Production Configuration

Create `backend/config.py`:

```python
import os

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", None)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
```

#### 3. Run with Gunicorn

```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 4. Serve Frontend with Nginx

Install Nginx and create configuration:

```nginx
# /etc/nginx/sites-available/land-records

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/Land Records/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/land-records /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option B: Docker Deployment

#### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### 3. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - SECRET_KEY=your-production-secret
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### 4. Deploy with Docker

```bash
docker-compose up -d
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | JWT signing key | (change in production) |
| API_PORT | Backend port | 8000 |
| CORS_ORIGINS | Allowed origins | * |

### Changing API URL

Edit `frontend/js/api.js`:

```javascript
const API = {
    baseURL: 'https://your-domain.com/api',
    // ...
};
```

---

## Security Considerations

### Production Checklist

- [ ] Change default SECRET_KEY
- [ ] Change default user passwords
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Restrict CORS_ORIGINS
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Set up logging and monitoring
- [ ] Regular backups of data files

### Adding HTTPS

Use Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Data Backup

### Manual Backup

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Copy data files
cp -r data/* backups/$(date +%Y%m%d)/
```

### Automated Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATA_DIR="/path/to/Land Records/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR/$DATE"
cp -r "$DATA_DIR"/* "$BACKUP_DIR/$DATE/"

# Keep only last 30 days
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +
```

Add to crontab:

```bash
0 2 * * * /path/to/backup.sh
```

---

## Monitoring

### Health Check

The API provides a health endpoint:

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "healthy",
  "service": "Land Record Digitization API",
  "version": "1.0.0"
}
```

### Log Files

Backend logs to stdout. Capture with:

```bash
uvicorn main:app 2>&1 | tee -a logs/app.log
```

---

## Updating the Application

### Update Steps

1. Stop services
2. Backup data
3. Pull/copy new code
4. Install updated dependencies
5. Restart services

```bash
# Stop
pkill -f uvicorn

# Backup
./backup.sh

# Update dependencies
pip install -e .

# Restart
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version

# Check if port is in use
netstat -tulpn | grep 8000

# Check logs for errors
uvicorn main:app --log-level debug
```

### Frontend Can't Connect to API

1. Verify API is running: `curl http://localhost:8000/`
2. Check browser console for CORS errors
3. Verify API URL in `api.js`
4. Check network firewall rules

### Data Not Loading

1. Verify data files exist in `data/` directory
2. Check file permissions
3. Validate JSON/CSV format
4. Check backend logs for parsing errors

---

## Support

For technical issues, check:

1. Application logs
2. Browser developer console
3. Network requests in DevTools

**Version:** 1.0.0
