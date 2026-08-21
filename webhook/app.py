from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os
import logging
import hmac
import hashlib
import json
from datetime import datetime
import requests

load_dotenv()

app = FastAPI()

# Config
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "5595319916"
LOG_FILE = "/home/tarun/orazen-trading-engine/webhook/events.log"

# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("webhook")


def verify_twenty_signature(raw_body: bytes, signature_header: str) -> bool:
    """Verify Twenty webhook HMAC-SHA256 signature."""
    if not WEBHOOK_SECRET:
        return True  # skip verification if no secret configured
    if not signature_header:
        raise HTTPException(status_code=403, detail="Missing signature header")
    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")
    return True


def send_telegram_notification(text: str):
    """Send a Telegram message using the Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass  # don't block webhook on notification failure


@app.post("/webhook/twenty")
async def twenty_webhook(request: Request):
    # Read raw body for signature verification
    raw_body = await request.body()

    # Verify signature if Twenty provides one
    signature = request.headers.get("X-Twenty-Signature", "")
    if signature:
        verify_twenty_signature(raw_body, signature)

    # Parse JSON
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("event_type", "unknown")
    contact = payload.get("data", {})

    # Only process contact.created and contact.updated
    if event_type not in ("contact.created", "contact.updated"):
        return {"ok": True}

    # Build log entry
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = json.dumps({
        "timestamp": timestamp,
        "event_type": event_type,
        "contact": contact,
    })

    # Log to file
    logger.info(log_entry)

    # Trigger Telegram notification
    contact_name = contact.get("name", "N/A")
    contact_email = contact.get("email", "N/A")
    notify_text = (
        f"*Twenty CRM Event*\n"
        f"`{event_type}`\n\n"
        f"Name: {contact_name}\n"
        f"Email: {contact_email}"
    )
    send_telegram_notification(notify_text)

    # Return 200 immediately
    return {"ok": True}
