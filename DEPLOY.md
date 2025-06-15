# Deploy Vehicle AI Backend to Render

## 🚀 Quick Deploy Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select this repository: `vehicle-ai-poc`
5. Configure the service:

**Basic Settings:**
- **Name**: `vehicle-ai-backend`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables
In the Render dashboard, go to **Environment** tab and add:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Deploy
Click **"Create Web Service"** and wait for deployment to complete.

## 📋 Deployment Files Created

✅ **render.yaml** - Render service configuration
✅ **runtime.txt** - Python 3.12.0 specification  
✅ **requirements.txt** - Updated Python dependencies (compatible with Python 3.12+)
✅ **Health check endpoints** - `/` and `/health`
✅ **CORS enabled** - For frontend integration
✅ **Environment variables** - OpenAI API key support

## 🔗 After Deployment

Your API will be available at:
```
https://vehicle-ai-backend.onrender.com
```

**Test endpoints:**
- Health check: `GET /`
- Detailed health: `GET /health`
- Single image: `POST /analyze`
- Batch images: `POST /analyze_batch`
- Training: `POST /train`

## 🛠️ Troubleshooting

**If deployment fails:**
1. Check build logs in Render dashboard
2. Verify all files are committed to GitHub
3. Ensure OpenAI API key is set correctly
4. Check Python version compatibility

**Common issues:**
- **Package compatibility**: Updated to use Python 3.12 compatible versions
- **OpenCV errors**: Using `opencv-python-headless==4.10.0.84` for server deployment
- **Port binding**: Uses `$PORT` environment variable automatically
- **File permissions**: Render handles this automatically
- **Dependencies**: All specified in requirements.txt with compatible versions

**Updated Package Versions (Python 3.12+ compatible):**
- FastAPI: 0.115.0
- Uvicorn: 0.32.0
- OpenCV: 4.10.0.84 (headless)
- NumPy: 2.1.0
- Pillow: 11.0.0
- Pydantic: 2.10.0

## 🔄 Auto-Deploy

The service is configured for auto-deploy. Every push to `main` branch will trigger a new deployment.

## 💰 Render Pricing

- **Free tier**: 750 hours/month (enough for testing)
- **Paid tier**: $7/month for always-on service
- **Scaling**: Automatic based on traffic

Your backend is production-ready! 🎉 