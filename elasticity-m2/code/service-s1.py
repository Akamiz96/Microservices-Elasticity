# service_s1.py
#!/usr/bin/env python3
"""
Microservice s1: CPU-bound compute engine.

Endpoints:
- GET /compute
  • Runs a recursive Fibonacci(25)
  • Returns JSON: { result: <number>, latency: <float> }
"""
from flask import Flask, jsonify
import time

app = Flask(__name__)

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

@app.route('/compute')
def compute():
    start = time.time()
    result = fib(25)
    latency = time.time() - start
    return jsonify({'result': result, 'latency': latency})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
