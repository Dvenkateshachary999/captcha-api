
import secrets
import time

captcha_store = {}

def generate_captcha():

    operations = ["+", "-", "*"]
    operation = secrets.choice(operations)

    if operation == "+":
        a = secrets.randbelow(20) + 1
        b = secrets.randbelow(20) + 1
        answer = a + b

    elif operation == "-":
        a = secrets.randbelow(20) + 10
        b = secrets.randbelow(10) + 1
        answer = a - b

    else:
        a = secrets.randbelow(10) + 1
        b = secrets.randbelow(10) + 1
        answer = a * b

    question = f"What is {a} {operation} {b}?"

    # Generate three incorrect options
    options = {answer}

    while len(options) < 4:
        offset = secrets.randbelow(10) + 1
        wrong_answer = answer + secrets.choice([-offset, offset])

        if wrong_answer >= 0:
            options.add(wrong_answer)

    options = list(options)
    secrets.SystemRandom().shuffle(options)

    captcha_id = secrets.token_urlsafe(16)

    captcha_store[captcha_id] = {
        "answer": str(answer),
        "created_at": time.time(),
        "attempts": 0
    }

    return {
        "captcha_id": captcha_id,
        "question": question,
        "options": [str(option) for option in options]
    }
