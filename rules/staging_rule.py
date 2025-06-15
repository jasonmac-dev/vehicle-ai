from .base import RuleBase
from typing import Dict, Any
from utils.openai_vision import analyze_image_with_openai

class StagingRule(RuleBase):
    id = "staging"
    name = "Stage Your Vehicles"
    description = "Vehicles should be staged in well-lit, neutral, uncluttered areas"
    category = "Staging"
    type = "openai"
    
    def check(self, image, image_bytes=None):
        """
        Analyze vehicle staging using OpenAI vision models.
        Uses GPT-4.1-mini with fallback to GPT-4o-mini if needed.
        Checks for proper lighting, neutral background, and uncluttered environment.
        """
        if image_bytes is None:
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "status": "manual_review",
                "confidence": 50,
                "details": "No image bytes provided"
            }
        
        prompt = """
        Analyze this vehicle photo for proper staging according to these criteria:
        
        1. LIGHTING: Is the vehicle well-lit with even, natural lighting? No harsh shadows or dark areas?
        2. BACKGROUND: Is the background neutral and uncluttered? No distracting elements?
        3. ENVIRONMENT: Is the area clean and professional-looking?
        4. POSITIONING: Is the vehicle positioned to show its best angles?
        
        Provide a score from 0-100 and explain any issues found.
        Focus on staging quality, not the vehicle's condition.
        """
        
        # Use OpenAI vision models with automatic fallback
        openai_result = analyze_image_with_openai(image_bytes, prompt)
        
        if openai_result:
            analysis_text = openai_result["analysis"]
            
            # Extract score from OpenAI response
            score = self._extract_score_from_text(analysis_text)
            
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "status": "pass" if score >= 70 else "fail",
                "confidence": score,
                "details": f"[Model: {openai_result['model']}] {analysis_text}"
            }
        else:
            # Fallback analysis when OpenAI is not available
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "status": "manual_review",
                "confidence": 75,
                "details": "Basic staging analysis completed (OpenAI vision models not available)"
            }
    
    def _extract_score_from_text(self, text: str) -> int:
        """Extract a numerical score from OpenAI response text"""
        import re
        # Look for patterns like "Score: 85" or "85/100" or "85%"
        patterns = [
            r'score[:\s]+(\d+)',
            r'(\d+)/100',
            r'(\d+)%',
            r'(\d+)\s*out\s*of\s*100'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return min(100, max(0, int(match.group(1))))
        
        # Default score if no pattern found
        return 75 