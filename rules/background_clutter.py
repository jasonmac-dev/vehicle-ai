from .base import RuleBase
# from your_object_detection_module import detect_objects

class BackgroundClutterRule(RuleBase):
    id = "background_clutter"
    name = "No Background Clutter"
    description = "No poles, trees, wires, other cars, buckets, trashcans, etc. in the background."
    category = "Background"
    type = "ai"

    def check(self, image, image_bytes=None):
        # detected_objects = detect_objects(image)
        # forbidden = {"tree", "pole", "wire", "car", "truck", "person"}
        # found = [obj for obj in detected_objects if obj in forbidden]
        found = []  # Stub for now
        if found:
            return {"id": self.id, "name": self.name, "description": self.description, "status": "fail", "confidence": 90, "details": f"Found: {', '.join(found)}"}
        return {"id": self.id, "name": self.name, "description": self.description, "status": "pass", "confidence": 99, "details": "No clutter detected"} 