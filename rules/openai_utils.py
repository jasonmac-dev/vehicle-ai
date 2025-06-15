import openai
import os
import base64
import logging
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

# Only initialize client if API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

# Debug logging for API key status
if not OPENAI_API_KEY:
    logger.warning("OpenAI API key not found in environment variables.")
    logger.debug("Available environment variables: %s", list(os.environ.keys()))
else:
    # Log masked API key for debugging (show first 8 and last 4 characters)
    masked_key = f"{OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}" if len(OPENAI_API_KEY) > 12 else "***masked***"
    logger.info(f"OpenAI API key found: {masked_key}")

if OPENAI_API_KEY:
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Could not initialize OpenAI client: {e}")
        client = None

def analyze_with_openai(image_bytes, prompt):
    if not client:
        logger.warning("OpenAI client not available")
        return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    # Try models in order of preference
    models_to_try = [
        "gpt-4.1-mini",  # Latest cost-effective model
        "gpt-4o-mini",   # Fallback option
        "gpt-4o"         # Last resort
    ]
    
    for model_name in models_to_try:
        try:
            logger.info(f"Attempting to use OpenAI model: {model_name}")
            
            # Convert image bytes to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a vehicle photo quality inspector."},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            logger.info(f"OpenAI {model_name} analysis completed successfully: {result[:100]}...")
            return f"[Model: {model_name}] {result}"
            
        except Exception as e:
            logger.warning(f"OpenAI {model_name} failed: {str(e)}")
            if model_name == models_to_try[-1]:  # Last model in list
                logger.error(f"All OpenAI models failed. Last error: {str(e)}")
                return f"OpenAI API error: {str(e)}"
            else:
                logger.info(f"Trying next model...")
                continue
    
    return "All OpenAI models failed" 