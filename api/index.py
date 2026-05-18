from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
import json, os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)

class Query(BaseModel):
    regions: list[str]
    threshold_ms: float

# Explicitly handle OPTIONS preflight (Vercel needs this)
@app.options("/")
def options():
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/")
def root():
    return JSONResponse(
        content={"status": "ok"},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.post("/")
def analyze(q: Query):
    result = {}
    for region in q.regions:
        records = [r for r in DATA if r["region"] == region]
        if not records:
            result[region] = {"error": "no data"}
            continue
        latencies = np.array([r["latency_ms"] for r in records])
        uptimes   = np.array([r["uptime_pct"]  for r in records])
        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime":  round(float(np.mean(uptimes)), 2),
            "breaches":    int(np.sum(latencies > q.threshold_ms)),
        }
    return JSONResponse(
        content=result,
        headers={"Access-Control-Allow-Origin": "*"}
    )
