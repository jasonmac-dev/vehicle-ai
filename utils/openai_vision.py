import openai
import os
import base64
import dotenv
import json
dotenv.load_dotenv()


def analyze_with_openai_multi(image_bytes: bytes, prompts: dict) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    # System-level instruction to avoid markdown/extra text
    system_prompt = {
        "role": "system",
        "content": (
            "You are a strict dealership photo evaluator. Only respond with a raw JSON array as described. "
            "Do not include markdown formatting, comments, or extra text. Each rule must be independently evaluated."
        )
    }

    # Combined user prompt with rule-specific evaluation tasks
    combined_prompt = (
        "You are given an image of a dealership vehicle. "
        "Based on the image, evaluate each rule below and respond with ONLY a JSON array using this format:\n\n"
        "[\n"
        "  {\n"
        "    \"ruleId\": \"vehicle_dressed\",\n"
        "    \"status\": \"pass|fail|unknown\",\n"
        "    \"confidence\": 0-100,\n"
        "    \"reason\": \"Brief explanation with visual justification\"\n"
        "  },\n"
        "  ...\n"
        "]\n\n"
    )

    for rule_id, prompt in prompts.items():
        combined_prompt += (
            f"\nEvaluate ruleId: \"{rule_id}\"\n"
            f"Instruction: {prompt}\n"
        )

    # Submit to OpenAI
    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            system_prompt,
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": combined_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }
        ],
        max_tokens=1000,
        temperature=0
    )

    return response.choices[0].message.content

def parse_openai_results(json_text: str) -> list:
    try:
        data = json.loads(json_text)
        for item in data:
            item["description"] = item.get("reason", "")
        return data
    except json.JSONDecodeError:
        return [{"id": "error", "status": "fail", "confidence": 0, "description": "Invalid JSON response"}]
# def parse_openai_results(raw_text: str, rule_prompts: dict) -> list:
#     results = []
#     text = raw_text.lower()

#     for rule_id, prompt in rule_prompts.items():
#         status = "unknown"
#         confidence = 50

#         if rule_id == "vehicle_staging":
#             if "well-lit" in text or "neutral background" in text or "staged properly" in text:
#                 status = "pass"
#                 confidence = 95
#             elif "poor lighting" in text or "messy environment" in text or "improperly staged" in text:
#                 status = "fail"
#                 confidence = 85

#         elif rule_id == "background_clutter":
#             if "no clutter" in text or "clean background" in text:
#                 status = "pass"
#                 confidence = 95
#             elif "clutter" in text or "trees" in text or "poles" in text or "trashcan" in text:
#                 status = "fail"
#                 confidence = 80

#         elif rule_id == "vehicle_cleanliness":
#             if "vehicle is clean" in text or "no visible dirt" in text or "free of smudges" in text:
#                 status = "pass"
#                 confidence = 95
#             elif "dirty" in text or "dust" in text or "smudges" in text or "unclean" in text:
#                 status = "fail"
#                 confidence = 85

#         elif rule_id == "vehicle_dressed":
#             positive_indicators = ["professionally arranged", "seats upright", "seats aligned", "headrests lowered"]
#             negative_indicators = [
#                 "uneven", "not aligned", "misaligned", "reclined while", "seat not upright",
#                 "one seat", "seat reclined", "seats appear off", "seats are not evenly aligned"
#             ]

#             if any(p in text for p in positive_indicators) and all(n not in text for n in negative_indicators):
#                 status = "pass"
#                 confidence = 95
#             elif any(n in text for n in negative_indicators):
#                 status = "fail"
#                 confidence = 85
#             elif "not visible" in text or "can't be seen" in text:
#                 status = "unknown"
#                 confidence = 50


#         elif rule_id == "image_steady_and_landscape":
#             if "sharp" in text and "landscape" in text:
#                 status = "pass"
#                 confidence = 95
#             elif "blurry" in text or "vertical" in text or "portrait" in text:
#                 status = "fail"
#                 confidence = 90

#         elif rule_id == "dealer_overlay_check":
#             if "no overlay" in text or "no dealer branding" in text:
#                 status = "pass"
#                 confidence = 95
#             elif "dealer overlay" in text or "logo visible" in text or "store phone number" in text:
#                 status = "fail"
#                 confidence = 85

#         results.append({
#             "id": rule_id,
#             "name": prompt,
#             "description": prompt,
#             "status": status,
#             "confidence": confidence,
#             "details": f"GPT-4 response: {raw_text}"
#         })

#     return results
