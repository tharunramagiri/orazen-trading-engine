from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import stripe
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

BASE = Path('/home/tarun/orazen-trading-engine/web')
(BASE / 'static').mkdir(exist_ok=True)

# Stripe config
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
TWENTY_WEBHOOK_SECRET = os.getenv('TWENTY_WEBHOOK_SECRET', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5595319916')

PRICES = {
    'starter': os.getenv('STRIPE_PRICE_STARTER', ''),
    'growth': os.getenv('STRIPE_PRICE_GROWTH', ''),
    'scale': os.getenv('STRIPE_PRICE_SCALE', ''),
}

# Logging
logging.basicConfig(
    filename='/home/tarun/orazen-trading-engine/webhook/events.log',
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger('webhook')


@app.get('/', response_class=HTMLResponse)
async def landing():
    return (BASE / 'index.html').read_text()


@app.get('/pricing', response_class=HTMLResponse)
async def pricing():
    return (BASE / 'pricing.html').read_text()


@app.post('/api/checkout')
async def checkout(request: Request):
    body = await request.json()
    plan = body.get('plan', 'starter')
    email = body.get('email', '')
    name = body.get('name', '')

    if not stripe.api_key:
        return JSONResponse({'error': 'Stripe not configured'}, status_code=500)

    price_id = PRICES.get(plan)
    if not price_id:
        return JSONResponse({'error': 'Invalid plan'}, status_code=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            customer_email=email,
            metadata={'plan': plan, 'contact_name': name},
            success_url='https://engine.orazen.online/success',
            cancel_url='https://engine.orazen.online/pricing',
        )
        return JSONResponse({'url': session.url})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)


@app.get('/health')
async def health():
    return {'status': 'ok', 'engine': 'orazen', 'version': '2026.8-dev'}


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

    if event_type in ('contact.created', 'contact.updated') and TELEGRAM_BOT_TOKEN:
        contact = data.get('record', data)
        name = contact.get('name', contact.get('firstName', 'New contact'))
        email = contact.get('email', '')
        text = f"CRM event: {event_type}\n{name}\n{email}"
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': text},
            timeout=10,
        )

    return JSONResponse({'ok': True})


@app.get('/success')
async def success():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Checkout Successful</title></head>
<body style="background:#0a0a0a;color:#f4f4f5;font-family:system-ui;padding:4rem;text-align:center;">
  <h1>Welcome to Orazen 🎉</h1>
  <p>Check your email to get started.</p>
</body>
</html>
    """)
