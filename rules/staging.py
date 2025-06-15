from .base import RuleBase
from .openai_utils import analyze_with_openai

class StagingRule(RuleBase):
    id = "stage_lighting"
    name = "Proper Staging & Lighting"
    description = "Vehicle is staged in a well-lit, neutral, uncluttered area."
    category = "Staging"
    type = "openai"

    def check(self, image, image_bytes=None):
        prompt = (
            "Is the vehicle staged in a well-lit, neutral, uncluttered area? "
            "Are there any distracting objects in the background?"
        )
        if image_bytes is None:
            return {"id": self.id, "name": self.name, "description": self.description, "status": "manual_review", "confidence": 50, "details": "No image bytes provided"}
        result = analyze_with_openai(image_bytes, prompt)
        # You can parse result for pass/fail if desired
        return {"id": self.id, "name": self.name, "description": self.description, "status": "manual_review", "confidence": 50, "details": result} 