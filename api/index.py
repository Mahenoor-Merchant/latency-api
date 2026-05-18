from http.server import BaseHTTPRequestHandler
import json, numpy as np, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
with open(DATA_PATH) as f:
    DATA = json.load(f)

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

class handler(BaseHTTPRequestHandler):

    def _send(self, code, body, extra_headers={}):
        self.send_response(code)
        for k, v in {**CORS, **extra_headers}.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_OPTIONS(self):
        self._send(200, "ok")

    def do_GET(self):
        self._send(200, {"status": "ok"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        regions = body["regions"]
        threshold = body["threshold_ms"]

        result = {}
        for region in regions:
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
                "breaches":    int(np.sum(latencies > threshold)),
            }

        self._send(200, result)
