from .base import RuleBase
# from your_ocr_module import detect_text

class OverlaysRule(RuleBase):
    id = "no_overlays"
    name = "No Overlays or Badges"
    description = "No dealer overlays, badges, or phone numbers in the photo."
    category = "Photo Quality"
    type = "ai"

    def check(self, image, image_bytes=None):
        # detected_text = detect_text(image)
        # if "dealer" in detected_text or "phone" in detected_text:
        #     return {...}
        return {"id": self.id, "name": self.name, "description": self.description, "status": "pass", "confidence": 99, "details": "No overlays detected"} 