from flask import Flask, request, jsonify
import os
import threading
from hasher import ConsistentHashRing
import docker_manager as dm
import requests

app = Flask(__name__)
ring = ConsistentHashRing()
replicas = set()
N = 3  # Initial number of replicas

def init_replicas(n=N):
    for i in range(1, n + 1):
        name = f"server{i}"
        server_id = i
        ring.add_server(server_id, name)
        replicas.add(name)

@app.route('/rep', methods=['GET'])
def get_replicas():
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": sorted(list(replicas))
        },
        "status": "successful"
    }), 200

@app.route('/add', methods=['POST'])
def add_replicas():
    data = request.get_json()
    n = data.get("n", 0)
    names = data.get("hostnames", [])

    if len(names) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    for i in range(n):
        name = names[i] if i < len(names) else dm.generate_random_name()
        if dm.spawn_container(name):
            server_id = 100 + i  # Ensure unique server IDs
            ring.add_server(server_id, name)
            replicas.add(name)

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": sorted(list(replicas))
        },
        "status": "successful"
    }), 200

@app.route('/rm', methods=['DELETE'])
def remove_replicas():
    data = request.get_json()
    n = data.get("n", 0)
    names = data.get("hostnames", [])

    if len(names) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    removable = list(names)
    others = list(replicas - set(removable))
    while len(removable) < n and others:
        removable.append(others.pop())

    for name in removable:
        dm.remove_container(name)
        replicas.discard(name)
        # Optional: remove server from hash ring if you track reverse map

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": sorted(list(replicas))
        },
        "status": "successful"
    }), 200

@app.route('/<path:req_path>', methods=['GET'])
def route_request(req_path):
    if not replicas:
        return jsonify({"message": "No servers available", "status": "failure"}), 500

    # Derive numeric ID from path for consistent hashing
    req_id = int(''.join(filter(str.isdigit, req_path)) or '100001')
    target = ring.get_server(req_id)

    if not target or target not in replicas:
        return jsonify({"message": "<Error> Could not find target", "status": "failure"}), 400

    try:
        resp = requests.get(f"http://{target}:5000/{req_path}")
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({
            "message": f"<Error> '{req_path}' endpoint does not exist in server replicas or failed to connect",
            "status": "failure",
            "detail": str(e)
        }), 400

if __name__ == '__main__':
    init_replicas()
    app.run(host='0.0.0.0', port=5000)
