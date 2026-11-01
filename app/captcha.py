
import random
import string
import secrets
import time

from PIL import Image, ImageDraw
from io import BytesIO


# Temporary storage for CAPTCHA answers
captcha_store = {}


def generate_captcha():

    captcha_text = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )

    captcha_id = secrets.token_urlsafe(16)

    # Store CAPTCHA answer and attempt count
    captcha_store[captcha_id] = {
        "answer": captcha_text,
        "created_at": time.time(),
        "attempts": 0
    }

    image = Image.new("RGB", (200, 80), "white")
    draw = ImageDraw.Draw(image)

    draw.text((35, 25), captcha_text, fill="black")

    for _ in range(5):
        x1 = random.randint(0, 200)
        y1 = random.randint(0, 80)
        x2 = random.randint(0, 200)
        y2 = random.randint(0, 80)

        draw.line(
            (x1, y1, x2, y2),
            fill="gray",
            width=1
        )

    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return captcha_id, image_bytes
