import json
import matplotlib.pyplot as plt

with open("analysis/results.json", "r") as f:
    data = json.load(f)

servers = list(data.keys())
counts = list(data.values())

plt.figure(figsize=(10, 6))
plt.bar(servers, counts, color='skyblue')
plt.xlabel("Server ID")
plt.ylabel("Requests Handled")
plt.title("A-1: Requests per Server (N=3)")
plt.tight_layout()
plt.savefig("analysis/bar_chart.png")
plt.show()
