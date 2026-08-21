from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE = Path('/home/tarun/orazen-trading-engine/web')
(BASE / 'static').mkdir(exist_ok=True)
app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')

@app.get('/', response_class=HTMLResponse)
async def landing():
    return (BASE / 'index.html').read_text()

@app.get('/pricing')
async def pricing():
    return JSONResponse({
        "plans": [
            {"name": "Starter", "price": "€49/mo", "features": ["Backtesting", "1 strategy", "Basic AI research"]},
            {"name": "Pro", "price": "€149/mo", "features": ["AI research", "5 strategies", "Hyperopt", "Priority support"]},
            {"name": "Institutional", "price": "€499/mo", "features": ["Live execution", "Dedicated AI agent", "API access", "Custom integrations"]},
        ]
    })

@app.get('/health')
async def health():
    return {"status": "ok", "engine": "orazen", "version": "2026.8-dev"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
