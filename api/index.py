from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import json, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)

class Query(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.get("/")
def root():
    return {"status": "ok"}

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
    return result
