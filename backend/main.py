import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
import dotenv

from . import database, gemini_service, priority_engine, policy_brief
from .live_feed import manager
from .models import CitizenRequest, SourceEnum
from .telegram_bot import setup_bot

dotenv.load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    
    # Calculate initial priorities if data exists
    reqs = await database.get_all_requests()
    dists = await database.get_districts()
    if reqs and dists:
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(None, priority_engine.calculate_priority_scores, reqs, dists)
        for s in scores:
            await database.upsert_priority_score(s)
            
    # Telegram Bot is now run via standalone run_bot.py to prevent conflicts
            
    yield

from .middleware import enterprise_security_middleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="JanSetu AI Backend", lifespan=lifespan)

# Enterprise Security Pipeline
app.add_middleware(BaseHTTPMiddleware, dispatch=enterprise_security_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_bot(app)

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class SubmitTextRequest(BaseModel):
    text: str
    source: str = "WEB"

@app.post("/api/submit-text")
async def submit_text(request: SubmitTextRequest):
    try:
        classification = gemini_service.classify_text(request.text)
        req = CitizenRequest(
            raw_text=request.text,
            translated_text=classification.translated_text,
            language_detected=classification.language,
            category=classification.category,
            location_district=classification.district,
            location_state=classification.state,
            urgency=classification.urgency,
            sentiment=classification.sentiment,
            latitude=classification.latitude,
            longitude=classification.longitude,
            source=SourceEnum(request.source)
        )
        req_id = await database.insert_request(req)
        
        # Broadcast real-time
        dump = req.model_dump()
        dump['id'] = req_id
        dump['timestamp'] = dump['timestamp'].isoformat() if dump.get('timestamp') else None
        await manager.broadcast_new_request(dump)
        
        return {"status": "success", "id": req_id, "classification": classification.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-voice")
async def submit_voice(file: UploadFile = File(...)):
    try:
        content = await file.read()
        mime_type = file.content_type or "audio/mpeg"
        classification = gemini_service.classify_audio(content, mime_type)
        req = CitizenRequest(
            raw_text="[Voice Message Web]",
            translated_text=classification.translated_text,
            language_detected=classification.language,
            category=classification.category,
            location_district=classification.district,
            location_state=classification.state,
            urgency=classification.urgency,
            sentiment=classification.sentiment,
            latitude=classification.latitude,
            longitude=classification.longitude,
            source=SourceEnum.WEB
        )
        req_id = await database.insert_request(req)
        return {"status": "success", "id": req_id, "classification": classification.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/requests")
async def get_requests(district: str = None, state: str = None, category: str = None, limit: int = 500):
    reqs = await database.get_all_requests()
    if district:
        reqs = [r for r in reqs if r['location_district'] == district]
    if state:
        reqs = [r for r in reqs if r['location_state'] == state]
    if category:
        reqs = [r for r in reqs if r['category'] == category]
    
    # Sort by ID descending (newest first) and limit to prevent frontend DOM freezing
    reqs = sorted(reqs, key=lambda x: x.get('id', 0), reverse=True)
    if limit:
        reqs = reqs[:limit]
        
    return reqs

@app.get("/api/districts")
async def get_districts():
    return await database.get_districts()

@app.get("/api/priorities")
async def get_priorities():
    scores = await database.get_priority_scores()
    for s in scores:
        if isinstance(s.get('category_breakdown'), str):
            s['category_breakdown'] = json.loads(s['category_breakdown'])
        if isinstance(s.get('top_issues'), str):
            s['top_issues'] = json.loads(s['top_issues'])
    return scores

@app.post("/api/recalculate")
async def recalculate():
    reqs = await database.get_all_requests()
    dists = await database.get_districts()
    loop = asyncio.get_running_loop()
    scores = await loop.run_in_executor(None, priority_engine.calculate_priority_scores, reqs, dists)
    for s in scores:
        await database.upsert_priority_score(s)
    return {"status": "success", "calculated_districts": len(scores)}

import asyncio
import random
from datetime import datetime

simulator_task = None

async def run_simulator():
    reqs = await database.get_all_requests()
    if not reqs:
        return
    
    while True:
        # Pick a random request as template
        base = random.choice(reqs)
        
        # Add slight jitter to coordinates for heatmap
        lat = (base.get('latitude') or 20.0) + random.uniform(-0.1, 0.1)
        lng = (base.get('longitude') or 78.0) + random.uniform(-0.1, 0.1)
        
        sim_req = CitizenRequest(
            raw_text=base.get('raw_text', 'Simulation'),
            translated_text=base.get('translated_text', 'Simulation'),
            language_detected=base.get('language_detected', 'Hindi'),
            category=base.get('category', 'ROADS'),
            location_district=base.get('location_district', 'Pune'),
            location_state=base.get('location_state', 'Maharashtra'),
            urgency=random.randint(1, 5),
            sentiment=base.get('sentiment', 'NEGATIVE'),
            latitude=lat,
            longitude=lng,
            source=SourceEnum.TELEGRAM
        )
        
        req_id = await database.insert_request(sim_req)
        
        dump = sim_req.model_dump()
        dump['id'] = req_id
        dump['timestamp'] = datetime.utcnow().isoformat()
        
        await manager.broadcast_new_request(dump)
        await asyncio.sleep(random.uniform(1.0, 3.0))

@app.post("/api/start-simulator")
async def start_simulator():
    global simulator_task
    if simulator_task is None or simulator_task.done():
        simulator_task = asyncio.create_task(run_simulator())
        return {"status": "Simulator started"}
    return {"status": "Simulator already running"}

@app.post("/api/stop-simulator")
async def stop_simulator():
    global simulator_task
    if simulator_task and not simulator_task.done():
        simulator_task.cancel()
        simulator_task = None
        return {"status": "Simulator stopped"}
    return {"status": "Simulator not running"}

@app.post("/api/generate-brief")
async def generate_brief():
    try:
        # Get latest priorities
        scores = await get_priorities()
        if not scores:
            raise HTTPException(status_code=400, detail="No data available")
            
        # Convert to objects
        from .models import DistrictPriority
        score_objs = [DistrictPriority(**s) for s in scores]
        
        md_content = gemini_service.generate_policy_brief(score_objs)
        pdf_bytes = policy_brief.generate_pdf(md_content)
        
        is_pdf = pdf_bytes.startswith(b'%PDF')
        media_type = "application/pdf" if is_pdf else "text/html"
        filename = "policy_brief.pdf" if is_pdf else "policy_brief.html"
        
        return Response(content=pdf_bytes, media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    reqs = await database.get_all_requests()
    total = len(reqs)
    
    languages = {}
    categories = {}
    
    for r in reqs:
        lang = r.get('language_detected', 'Unknown')
        languages[lang] = languages.get(lang, 0) + 1
        
        cat = r.get('category')
        categories[cat] = categories.get(cat, 0) + 1
        
    scores = await get_priorities()
    top_districts = scores[:5] if scores else []
    
    return {
        "total_requests": total,
        "languages": languages,
        "categories": categories,
        "top_districts": top_districts
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
