import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import cv2
import numpy as np
import json
import os
from datetime import datetime
import uuid
import pprint
from dotenv import load_dotenv
from utils.openai_vision import analyze_with_openai_multi, parse_openai_results
import re
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directories if they don't exist
os.makedirs("data/images", exist_ok=True)
os.makedirs("data/training", exist_ok=True)

class TrainingFeedback(BaseModel):
    ruleId: str
    isCorrect: bool
    imageId: str

# Load or initialize rules
RULES_FILE = "data/rules.json"
if os.path.exists(RULES_FILE):
    with open(RULES_FILE, "r") as f:
        RULES = json.load(f)
else:
    RULES = [
        {
            "id": "rule1",
            "name": "Image Quality",
            "description": "Check if the image is clear and well-lit",
            "threshold": 0.7
        },
        {
            "id": "rule2",
            "name": "Vehicle Visibility",
            "description": "Ensure the entire vehicle is visible in the frame",
            "threshold": 0.8
        },
        {
            "id": "rule3",
            "name": "Background Clarity",
            "description": "Check if the background is clear and not cluttered",
            "threshold": 0.6
        }
    ]
    with open(RULES_FILE, "w") as f:
        json.dump(RULES, f, indent=2)

def analyze_image(image: np.ndarray) -> dict:
    """Analyze the image using various computer vision techniques"""
    results = {
        "rules": [],
        "overallScore": 0,
        "suggestions": [],
        "metadata": {
            "imageSize": image.nbytes,
            "dimensions": {
                "width": image.shape[1],
                "height": image.shape[0]
            },
            "format": "JPEG"
        }
    }

    # Convert to grayscale for some analyses
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Rule 1: Image Quality (using blur detection)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    quality_score = min(1.0, blur_score / 500)  # Normalize blur score
    results["rules"].append({
        "id": "rule1",
        "name": "Image Quality",
        "description": "Check if the image is clear and well-lit",
        "status": "pass" if quality_score > RULES[0]["threshold"] else "fail",
        "confidence": round(quality_score * 100, 2)
    })

    # Rule 2: Vehicle Visibility (using edge detection)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.count_nonzero(edges) / (image.shape[0] * image.shape[1])
    visibility_score = min(1.0, edge_density * 10)  # Normalize edge density
    results["rules"].append({
        "id": "rule2",
        "name": "Vehicle Visibility",
        "description": "Ensure the entire vehicle is visible in the frame",
        "status": "pass" if visibility_score > RULES[1]["threshold"] else "fail",
        "confidence": round(visibility_score * 100, 2)
    })

    # Rule 3: Background Clarity (using color variance)
    color_std = np.std(image, axis=(0, 1))
    background_score = min(1.0, np.mean(color_std) / 100)  # Normalize color variance
    results["rules"].append({
        "id": "rule3",
        "name": "Background Clarity",
        "description": "Check if the background is clear and not cluttered",
        "status": "pass" if background_score > RULES[2]["threshold"] else "fail",
        "confidence": round(background_score * 100, 2)
    })

    # Calculate overall score
    results["overallScore"] = round(
        sum(rule["confidence"] for rule in results["rules"]) / len(results["rules"]),
        2
    )

    # Generate suggestions based on analysis
    if quality_score < RULES[0]["threshold"]:
        results["suggestions"].append("Consider taking the photo in better lighting conditions")
    if visibility_score < RULES[1]["threshold"]:
        results["suggestions"].append("Ensure the entire vehicle is visible in the frame")
    if background_score < RULES[2]["threshold"]:
        results["suggestions"].append("Try to take the photo against a cleaner background")

    return results

@app.post("/analyze")
async def analyze_photo(image: UploadFile = File(...), training_mode: bool = False):
    try:
        # Read and validate image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Generate unique ID for the image
        image_id = str(uuid.uuid4())
        
        # Save image if in training mode
        if training_mode:
            image_path = f"data/images/{image_id}.jpg"
            cv2.imwrite(image_path, img)

        # Analyze image
        results = analyze_image(img)
        results["metadata"]["imageId"] = image_id

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_model(feedback: TrainingFeedback):
    try:
        # Save training feedback
        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "ruleId": feedback.ruleId,
            "isCorrect": feedback.isCorrect,
            "imageId": feedback.imageId
        }
        
        feedback_file = f"data/training/{feedback.imageId}_{feedback.ruleId}.json"
        with open(feedback_file, "w") as f:
            json.dump(feedback_data, f, indent=2)

        # Update rule threshold based on feedback
        for rule in RULES:
            if rule["id"] == feedback.ruleId:
                # Adjust threshold based on feedback
                if feedback.isCorrect:
                    rule["threshold"] *= 0.95  # Make it slightly easier to pass
                else:
                    rule["threshold"] *= 1.05  # Make it slightly harder to pass
                break

        # Save updated rules
        with open(RULES_FILE, "w") as f:
            json.dump(RULES, f, indent=2)

        return {"status": "success", "message": "Training feedback recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


OPENAI_RULES = {
    "vehicle_staging": "Is the vehicle staged in a clean, well-lit, and distraction-free environment (e.g., studio, garage, or a south-facing wall)?",
    "background_clutter": "Does the background include any distracting objects such as poles, wires, other cars, trashcans, or clutter?",
    "vehicle_cleanliness": "Is the vehicle clean and free of dirt, dust, smudges, or foreign objects (e.g., jackets, water bottles, paper floor mats)?",
    "vehicle_dressed": (
    "Is the vehicle interior professionally arranged? Specifically check for:\n"
    "- Headrests are lowered\n"
    "- Front seats are evenly aligned and upright\n"
    "- Folding rear seats are upright\n"
    "- No windshield stickers or dealer tags\n"
    "- Navigation screen is on\n"
    "If the front seats are not aligned or upright, mark this as 'fail' and explain."
     ),  
    "image_steady_and_landscape": "Is the image sharp, taken in landscape orientation, and free from blur or motion artifacts?",
    "dealer_overlay_check": "Do the images include any dealer overlays, badges, logos, or watermarks (e.g., store name, phone number, 'fresh trade' tags)?"
}
def extract_json_block(text: str) -> str:
    """
    Extracts the first JSON array found in a string.
    """
    match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
    return match.group(0) if match else "[]"
@app.post("/analyze_batch")
async def analyze_batch(images: List[UploadFile] = File(...), training_mode: bool = False):
    results = []

    for image in images:
        try:
            contents = await image.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Invalid image file")

            image_id = str(uuid.uuid4())
            if training_mode:
                cv2.imwrite(f"data/images/{image_id}.jpg", img)

            # 🔥 OpenAI multi-rule vision evaluation
            gpt_response = analyze_with_openai_multi(contents, OPENAI_RULES)
            print("🔍 GPT response:", gpt_response)
            json_block = extract_json_block(gpt_response)
            rule_results = parse_openai_results(json_block)

            overall_score = round(
                sum(rule.get("confidence", 0) for rule in rule_results) / len(rule_results), 2
            )
            suggestions = [r["description"] for r in rule_results if r["status"] == "fail"]

            results_dict = {
                "rules": rule_results,
                "overallScore": overall_score,
                "suggestions": suggestions,
                "metadata": {
                    "imageSize": img.nbytes,
                    "dimensions": {"width": img.shape[1], "height": img.shape[0]},
                    "format": "JPEG",
                    "imageId": image_id,
                    "filename": image.filename
                }
            }
            results.append(results_dict)

        except Exception as e:
            results.append({
                "error": str(e),
                "rules": [],
                "overallScore": 0,
                "suggestions": [],
                "metadata": {
                    "imageSize": 0,
                    "dimensions": {"width": 0, "height": 0},
                    "format": "",
                    "imageId": None,
                    "filename": image.filename
                }
            })

    pprint.pprint(results)
    return {"results": results}

@app.get("/")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "service": "vehicle-ai-backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def detailed_health_check():
    """Detailed health check with system status"""
    openai_status = "available" if os.getenv('OPENAI_API_KEY') else "not_configured"
    
    return {
        "status": "healthy",
        "service": "vehicle-ai-backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "openai_status": openai_status,
        "rules_loaded": len(RULES),
        "data_directories": {
            "images": os.path.exists("data/images"),
            "training": os.path.exists("data/training")
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 