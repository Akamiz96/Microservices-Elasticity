#!/usr/bin/env python3
"""
Microservicio s0: calcula fib(n) y devuelve resultado + latencia.
Endpoint:
  GET /compute?n=<entero>  (por defecto n=25)
Respuesta:
  { "result": <número>, "latency": <segundos> }
"""
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

@app.route('/compute')
def compute():
    n = int(request.args.get('n', 25))
    start = time.time()
    result = fib(n)
    latency = time.time() - start
    return jsonify({"result": result, "latency": latency})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
