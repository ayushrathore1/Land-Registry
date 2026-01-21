# Land Record Digitization Tool

A web-based application for correlating textual land records with spatial parcel boundaries, flagging discrepancies for verification.

[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/land-records&root-directory=frontend)
[![Deploy Backend](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Features

- 🔍 **Search Interface** - Search by plot ID or owner name with fuzzy matching
- 🗺️ **Interactive Map** - Visualize parcels with color-coded match status
- 📊 **Reconciliation Analysis** - Compare textual and spatial records
- ✏️ **Editing Interface** - Authorized users can update records
- 📋 **Reports** - Generate and export reconciliation reports

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+ (recommended: 3.11)
- Modern web browser (Chrome, Firefox, Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/land-records.git
cd land-records
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the backend server**
```bash
python app.py
```
Server runs at: http://localhost:8000

4. **Serve the frontend** (in a new terminal)
```bash
cd frontend
python -m http.server 3000
```
App runs at: http://localhost:3000

---

## Deployment

### Frontend - Deploy to Vercel

1. **Push to GitHub** (fork or create new repo)

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Click Deploy

3. **Update API URL**
   - Edit `frontend/js/config.js`
   - Replace the production URL with your Render backend URL

### Backend - Deploy to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up or login

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: land-records-api
     - **Root Directory**: backend
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Set Environment Variables**
   - Add `SECRET_KEY` with a secure random value

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Copy your service URL (e.g., `https://land-records-api.onrender.com`)

5. **Update Frontend Config**
   - In `frontend/js/config.js`, update the production API URL

---

## Project Structure

```
land-records/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   └── render.yaml         # Render deployment config
├── frontend/
│   ├── index.html          # Main page
│   ├── styles.css          # Styling
│   ├── vercel.json         # Vercel config
│   └── js/
│       ├── config.js       # API URL configuration
│       ├── api.js          # API client
│       ├── app.js          # Main controller
│       └── ...             # Other modules
├── data/
│   ├── spatial/            # GeoJSON parcel data
│   └── textual/            # CSV land records
└── docs/                   # Documentation
```

## Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Data Schema](docs/DATA_SCHEMA.md)
- [User Guide](docs/USER_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## Test Accounts

| Username | Password | Role |
|----------|----------|------|
| viewer1 | viewer123 | View only |
| editor1 | editor123 | Can edit records |
| admin1 | admin123 | Full access |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, Flask |
| Frontend | JavaScript, Leaflet |
| Name Matching | RapidFuzz |
| Mapping | OpenStreetMap |
| Authentication | JWT |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | System statistics |
| `/api/search/plot?q=` | GET | Search by plot ID |
| `/api/search/owner?q=` | GET | Search by owner name |
| `/api/parcels/geojson` | GET | All parcels as GeoJSON |
| `/api/reconciliation/stats` | GET | Match/mismatch stats |
| `/api/reconciliation/report` | GET | Full report |
| `/api/auth/login` | POST | User login |

## Environment Variables

### Backend (Render)
| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key | Yes |

### Frontend (Vercel)
Configure API URL in `js/config.js`

## License

MIT License - See [LICENSE](LICENSE) for details.

## Version

1.0.0
