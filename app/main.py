
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.captcha import generate_captcha, captcha_store

# Create FastAPI application
app = FastAPI(title="CAPTCHA API")


# Request model
class CaptchaVerifyRequest(BaseModel):
    captcha_id: str
    answer: str


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to CAPTCHA API",
        "status": "Running"
    }


# Health Check API
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Generate CAPTCHA API
@app.get("/captcha/generate")
def captcha_generate():
    captcha_id, image_bytes = generate_captcha()

    return StreamingResponse(
        image_bytes,
        media_type="image/png",
        headers={"X-Captcha-ID": captcha_id}
    )


# Verify CAPTCHA API
@app.post("/captcha/verify")
def captcha_verify(request: CaptchaVerifyRequest):

    captcha_data = captcha_store.get(request.captcha_id)

    if captcha_data is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid or already used CAPTCHA ID"
        )

    # Check whether CAPTCHA has expired
    if time.time() - captcha_data["created_at"] > 120:
        captcha_store.pop(request.captcha_id, None)

        raise HTTPException(
            status_code=400,
            detail="CAPTCHA has expired. Please generate a new CAPTCHA."
        )

    # Verify CAPTCHA answer
    if captcha_data["answer"] == request.answer.strip().upper():
        captcha_store.pop(request.captcha_id, None)

        return {
            "success": True,
            "message": "CAPTCHA verified successfully"
        }

    # Increase incorrect attempt count
    captcha_data["attempts"] += 1

    # Invalidate after 3 incorrect attempts
    if captcha_data["attempts"] >= 3:
        captcha_store.pop(request.captcha_id, None)

        return {
            "success": False,
            "message": "Maximum 3 incorrect attempts reached. Please generate a new CAPTCHA."
        }

    return {
        "success": False,
        "message": f"Incorrect CAPTCHA. Attempts remaining: {3 - captcha_data['attempts']}"
    }
