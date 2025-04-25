# service_s0.py
#!/usr/bin/env python3
"""
Microservice s0: Lightweight text processor and orchestrator.

Endpoints:
- GET /process?text=<string>
  • Converts input text to uppercase
  • Calls s1 at /compute
  • Returns JSON: { text: <UPPER_TEXT>, result: <number>, latency_s1: <float> }
"""
from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)
S1_URL = 'http://service-s1.elasticity-m2.svc.cluster.local/compute'

@app.route('/process')
def process():
    text = request.args.get('text', '')
    processed = text.upper()

    start = time.time()
    resp = requests.get(S1_URL)
    latency_s1 = time.time() - start
    data = resp.json()

    return jsonify({
        'text':       processed,
        'result':     data.get('result'),
        'latency_s1': latency_s1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
