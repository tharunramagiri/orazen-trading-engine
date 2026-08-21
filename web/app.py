from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

app = FastAPI()

BASE = Path('/home/tarun/orazen-trading-engine/web')
(BASE / 'static').mkdir(exist_ok=True)
app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')

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

    # Stripe placeholder — replace with actual Stripe integration
    # For now, redirect to a placeholder
    return JSONResponse({
        "url": f"/checkout-placeholder?plan={plan}&email={email}&name={name}"
    })

@app.get('/checkout-placeholder')
async def checkout_placeholder():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Checkout</title></head>
<body style="background:#0a0a0a;color:#f4f4f5;font-family:system-ui;padding:4rem;text-align:center;">
  <h1>Stripe Integration Pending</h1>
  <p>This will redirect to Stripe Checkout once configured.</p>
  <p style="color:#a1a1aa;">Contact info@orazen.online to get early access.</p>
</body>
</html>
    """)

@app.get('/health')
async def health():
    return {"status": "ok", "engine": "orazen", "version": "2026.8-dev"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', '3000')))
