from flask import Flask, request, jsonify
import os, subprocess, random
from consistent_hash import ConsistentHash

app = Flask(__name__)

M = 512
N = 3
K = 9
hash_ring = ConsistentHash(replicas=K, slots=M)
replicas = {}

# Start initial servers
for i in range(1, N + 1):
    name = f"Server{i}"
    os.system(f"docker run -d --name {name} --network net1 -e SERVER_ID={name} server-image")
    replicas[name] = True
    hash_ring.add_server(name)

@app.route('/rep', methods=['GET'])
def get_replicas():
    return jsonify({"message": {"N": len(replicas), "replicas": list(replicas)}, "status": "successful"})

@app.route('/add', methods=['POST'])
def add_server():
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({"message": "<Error> Length of hostname list is more than newly added instances", "status": "failure"}), 400

    for i in range(n):
        name = hostnames[i] if i < len(hostnames) else f"S{random.randint(1000,9999)}"
        os.system(f"docker run -d --name {name} --network net1 -e SERVER_ID={name} server-image")
        replicas[name] = True
        hash_ring.add_server(name)

    return jsonify({"message": {"N": len(replicas), "replicas": list(replicas)}, "status": "successful"})

@app.route('/rm', methods=['DELETE'])
def remove_server():
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({"message": "<Error> Length of hostname list is more than removable instances", "status": "failure"}), 400

    removed = set()
    for name in hostnames[:n]:
        if name in replicas:
            os.system(f"docker rm -f {name}")
            hash_ring.remove_server(name)
            replicas.pop(name)
            removed.add(name)

    for name in list(replicas):
        if len(removed) >= n:
            break
        if name not in removed:
            os.system(f"docker rm -f {name}")
            hash_ring.remove_server(name)
            replicas.pop(name)
            removed.add(name)

    return jsonify({"message": {"N": len(replicas), "replicas": list(replicas)}, "status": "successful"})

@app.route('/<path:path>', methods=['GET'])
def route_request(path):
    req_id = str(random.randint(100000, 999999))
    target = hash_ring.get_server(req_id)
    try:
        res = subprocess.check_output(["curl", f"http://{target}:5000/{path}"])
        return res, 200
    except Exception:
        return jsonify({"message": f"<Error> '/{path}' endpoint does not exist in server replicas", "status": "failure"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
