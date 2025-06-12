from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Dict

from openai import OpenAI

from .config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from .utils import rate_limited

CLIENT = OpenAI()

EMAIL_PROMPT = "You are a friendly AI researcher reaching out to {receiver_name}. Context: you admired their paper '{paper_title}'. Goal: propose a quick chat about LLM pre-training research. Keep it concise (<120 words), personalise, add opt-out line."


def generate_body(name: str, lab: str, paper_title: str) -> str:
    resp = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": EMAIL_PROMPT.format(
                    receiver_name=name, paper_title=paper_title
                ),
            }
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content or ""


@rate_limited(120)
def send_email(to_name: str, to_email: str, context: Dict) -> None:
    body = generate_body(
        to_name, str(context.get("lab", "")), str(context.get("paper_title", ""))
    )
    msg = EmailMessage()
    msg["Subject"] = "LLM research collaboration"
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["List-Unsubscribe"] = "<mailto:unsubscribe@example.com>"
    msg.set_content(body + "\n\nPrivacy: https://example.com/privacy")
    with smtplib.SMTP(str(SMTP_HOST or ""), SMTP_PORT) as s:
        s.starttls()
        s.login(str(SMTP_USERNAME or ""), str(SMTP_PASSWORD or ""))
        s.send_message(msg)
