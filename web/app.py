from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import hmac
import hashlib
import json
import logging
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).parent
(BASE / 'static').mkdir(exist_ok=True)

TWENTY_WEBHOOK_SECRET = os.getenv('TWENTY_WEBHOOK_SECRET', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5595319916')

BETA_LEADS = BASE / 'static' / 'beta_leads.jsonl'

# Logging
LOG_FILE = BASE.parent / 'webhook' / 'events.log'
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger('webhook')


@app.get('/', response_class=HTMLResponse)
async def landing():
    return (BASE / 'beta.html').read_text()


@app.get('/pricing', response_class=HTMLResponse)
async def pricing():
    return (BASE / 'beta.html').read_text()


@app.post('/api/beta-join')
async def beta_join(request: Request):
    body = await request.json()
    email = (body.get('email') or '').strip().lower()
    if not email or '@' not in email:
        return JSONResponse({'message': 'Please enter a valid email.'}, status_code=400)

    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'email': email,
        'source': 'engine.orazen.online',
    }
    with BETA_LEADS.open('a') as f:
        f.write(json.dumps(entry) + '\n')

    if TELEGRAM_BOT_TOKEN:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': f"New Orazen beta signup: {email}"},
                timeout=10,
            )
        except Exception:
            pass

    return JSONResponse({'message': "You're on the list. We'll be in touch."})


@app.get('/health')
async def health():
    return {'status': 'ok', 'engine': 'orazen', 'version': '2026.8-beta'}


@app.post('/webhook/twenty')
async def twenty_webhook(request: Request):
    raw = await request.body()
    signature = request.headers.get('X-Twenty-Signature', '')

    if TWENTY_WEBHOOK_SECRET:
        expected = hmac.new(
            TWENTY_WEBHOOK_SECRET.encode('utf-8'),
            raw,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=403, detail='Invalid signature')

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid JSON')

    event_type = payload.get('eventType', 'unknown')
    data = payload.get('data', {})
    log_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'event_type': event_type,
        'data': data,
    }
    logger.info(json.dumps(log_entry))

    contact = data.get('record', data)
    name = contact.get('name', contact.get('firstName', 'New contact'))
    email = contact.get('email', '')

    if TELEGRAM_BOT_TOKEN:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': f"CRM event: {event_type}\n{name}\n{email}"},
                timeout=10,
            )
        except Exception:
            pass

    return JSONResponse({'ok': True})


@app.get('/success')
async def success():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Welcome to Orazen</title></head>
<body style="background:#0a0a0a;color:#f4f4f5;font-family:system-ui;padding:4rem;text-align:center;">
  <h1>You're on the list 🎉</h1>
  <p>We'll email you when your beta access is ready.</p>
</body>
</html>
    """)
