
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

from app.captcha import generate_captcha, captcha_store

app = FastAPI(title="Question Based CAPTCHA API")


class VerifyRequest(BaseModel):
    captcha_id: str
    answer: str


@app.get("/")
def home():
    return {
        "message": "Welcome to Question Based CAPTCHA API",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/captcha/generate")
def create_captcha():
    return generate_captcha()


@app.post("/captcha/verify")
def verify_captcha(request: VerifyRequest):

    captcha = captcha_store.get(request.captcha_id)

    if not captcha:
        raise HTTPException(
            status_code=404,
            detail="Invalid CAPTCHA ID"
        )

    if time.time() - captcha["created_at"] > 120:
        del captcha_store[request.captcha_id]
        raise HTTPException(
            status_code=410,
            detail="CAPTCHA expired. Generate a new one."
        )

    if captcha["attempts"] >= 3:
        del captcha_store[request.captcha_id]
        raise HTTPException(
            status_code=429,
            detail="Maximum attempts exceeded"
        )

    if request.answer.strip() == captcha["answer"]:
        del captcha_store[request.captcha_id]
        return {
            "success": True,
            "message": "CAPTCHA verified successfully"
        }

    captcha["attempts"] += 1

    return {
        "success": False,
        "message": "Incorrect answer",
        "attempts_remaining": 3 - captcha["attempts"]
    }
