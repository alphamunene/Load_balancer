import os
import json
import asyncio
import aiohttp
import time
import matplotlib.pyplot as plt
from collections import defaultdict

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            res = await response.json()
            return res["message"].split(": ")[-1]
    except:
        return "Error"

async def run_requests(n_requests, endpoint):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, endpoint) for _ in range(n_requests)]
        results = await asyncio.gather(*tasks)
        return results

N_REQUESTS = 10000
scales = list(range(2, 7))
average_loads = []

for N in scales:
    os.system("docker-compose down")
    os.system("docker-compose up -d --build")
    os.system("sleep 5")  # Wait for servers to boot

    # Adjust server count
    payload = {"n": N-3, "hostnames": [f"S{i}" for i in range(4, N+1)]}
    os.system(f'curl -X POST -H "Content-Type: application/json" -d '{json.dumps(payload)}' http://localhost:5000/add')

    time.sleep(3)
    results = asyncio.run(run_requests(N_REQUESTS, "http://localhost:5000/home"))
    counts = defaultdict(int)
    for server in results:
        counts[server] += 1

    avg = sum(counts.values()) / len(counts)
    average_loads.append(avg)

plt.plot(scales, average_loads, marker='o')
plt.xlabel("Number of Servers (N)")
plt.ylabel("Average Load per Server")
plt.title("A-2: Average Load vs Server Count")
plt.grid(True)
plt.tight_layout()
plt.savefig("analysis/line_chart.png")
plt.show()
