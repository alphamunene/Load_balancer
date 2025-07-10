import asyncio
import aiohttp
import time
import json
from collections import defaultdict

N_REQUESTS = 10000
ENDPOINT = "http://localhost:5000/home"
CONCURRENCY = 100

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            res = await response.json()
            return res["message"].split(": ")[-1]
    except:
        return "Error"

async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch(session, url)

async def run():
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(bound_fetch(sem, session, ENDPOINT)) for _ in range(N_REQUESTS)]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == '__main__':
    start = time.time()
    results = asyncio.run(run())
    duration = time.time() - start

    counts = defaultdict(int)
    for server in results:
        counts[server] += 1

    with open("analysis/results.json", "w") as f:
        json.dump(counts, f, indent=2)

    print(f"Completed {N_REQUESTS} requests in {duration:.2f} seconds.")
    print(json.dumps(counts, indent=2))
