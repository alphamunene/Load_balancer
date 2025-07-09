from flask import Flask, request, jsonify
import os
import threading
from hasher import ConsistentHashRing
import docker_manager as dm
import requests

app = Flask(__name__)
ring = ConsistentHashRing()
replicas = set()
N = 3

def init_replicas(n=N):
    for i in range(1, n + 1):
        name = f"server{i}"
        ring.add_server(i)
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
            ring.add_server(i + 100)
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

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": sorted(list(replicas))
        },
        "status": "successful"
    }), 200

@app.route('/home', methods=['GET'])
def route_home():
    if not replicas:
        return jsonify({"message": "No servers available", "status": "failure"}), 500

    req_id = request.args.get('id', default='100001')
    sid = ring.get_server(req_id)

    # Find server containing the sid
    target = None
    for name in replicas:
        if str(sid) in name:
            target = name
            break

    if not target:
        return jsonify({"message": "<Error> Could not find target", "status": "failure"}), 400

    try:
        resp = requests.get(f"http://{target}:5000/home")
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"message": "<Error> Failed to connect to target server", "status": "failure"}), 400

if __name__ == '__main__':
    init_replicas()
    app.run(host='0.0.0.0', port=5000)
