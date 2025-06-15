# Vehicle AI Photo QA Backend

A production-ready FastAPI backend for analyzing vehicle photos against quality assurance rules using AI vision models.

## 🚀 Features

- **Multi-Image Batch Processing**: Analyze multiple vehicle photos simultaneously
- **AI-Powered Analysis**: Uses OpenAI GPT-4.1-mini with fallback models
- **Modular Rule Engine**: Extensible rule system for different QA criteria
- **Training Mode**: Collect user feedback for continuous improvement
- **Production Ready**: Configured for Render deployment
- **Health Monitoring**: Built-in health check endpoints

## 📋 Vehicle QA Rules

The system analyzes photos against 6 main categories:

1. **Stage Your Vehicles** - Well-lit, neutral, uncluttered areas
2. **Clean Backgrounds** - No poles, trees, wires, other cars, etc.
3. **Clean the Vehicle** - Fully detailed, no dust/dirt/grime
4. **Dress the Vehicle** - Remove stickers, position seats/steering, no warning lights
5. **Steady Camera/Device** - No blurry photos, landscape orientation
6. **Upload Photos** - No overlays, badges, phone numbers

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4.1-mini** - Latest vision model with fallbacks
- **OpenCV** - Computer vision processing
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd vehicle-ai-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
# Create .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 4. Run Development Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health Checks
- `GET /` - Basic health check
- `GET /health` - Detailed system status

### Image Analysis
- `POST /analyze` - Analyze single image
- `POST /analyze_batch` - Analyze multiple images

### Training
- `POST /train` - Submit training feedback

## 📝 API Usage Examples

### Single Image Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@vehicle.jpg" \
  -F "training_mode=false"
```

### Batch Image Analysis
```bash
curl -X POST "http://localhost:8000/analyze_batch" \
  -H "Content-Type: multipart/form-data" \
  -F "images=@vehicle1.jpg" \
  -F "images=@vehicle2.jpg" \
  -F "training_mode=false"
```

## 🏗️ Project Structure

```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version for deployment
├── render.yaml            # Render deployment config
├── rules/                 # Rule engine modules
│   ├── __init__.py
│   ├── base.py           # Base rule class
│   ├── staging.py        # Vehicle staging rules
│   ├── background_clutter.py
│   ├── overlays.py
│   └── openai_utils.py   # OpenAI integration
├── utils/                # Utility modules
│   └── openai_vision.py  # OpenAI vision utilities
└── data/                 # Runtime data (gitignored)
    ├── images/           # Uploaded images
    ├── training/         # Training feedback
    └── rules.json        # Dynamic rule configuration
```

## 🚀 Deploy to Render

### Quick Deploy
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect your repository
5. Set **Root Directory**: `backend`
6. Add **Environment Variable**: `OPENAI_API_KEY`
7. Deploy!

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for AI analysis
- `PORT` - Server port (auto-set by Render)

### Rule Configuration
Rules are dynamically loaded from `data/rules.json` and can be updated via the training API.

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Test with Sample Image
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_vehicle.jpg"
```

## 🤖 AI Models

### Primary Model: GPT-4.1-mini
- Latest 2025 OpenAI vision model
- 83% cost reduction vs GPT-4o
- 50% faster response times
- Automatic fallback to GPT-4o-mini and GPT-4o

### Fallback Strategy
1. **GPT-4.1-mini** (primary)
2. **GPT-4o-mini** (fallback)
3. **GPT-4o** (final fallback)
4. **Manual review** (if all AI fails)

## 📊 Response Format

```json
{
  "results": [
    {
      "rules": [
        {
          "id": "vehicle_staging",
          "name": "Stage Your Vehicles",
          "status": "pass",
          "confidence": 85,
          "description": "Vehicle is well-staged"
        }
      ],
      "overallScore": 85.5,
      "suggestions": [],
      "metadata": {
        "imageId": "uuid-here",
        "filename": "vehicle.jpg",
        "dimensions": {"width": 1920, "height": 1080}
      }
    }
  ]
}
```

## 🔄 Training Mode

Enable continuous learning by setting `training_mode=true`:
- Saves uploaded images for review
- Collects user feedback via `/train` endpoint
- Adjusts rule thresholds based on feedback
- Improves accuracy over time

## 🛡️ Security

- Environment variables for sensitive data
- Input validation with Pydantic
- File type validation for uploads
- CORS configuration for frontend integration

## 📈 Monitoring

- Health check endpoints for uptime monitoring
- Detailed system status including OpenAI connectivity
- Request/response logging
- Error handling with proper HTTP status codes

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section in [DEPLOY.md](DEPLOY.md)
2. Review API documentation above
3. Check server logs for detailed error messages

---

**Ready for production deployment!** 🚀 