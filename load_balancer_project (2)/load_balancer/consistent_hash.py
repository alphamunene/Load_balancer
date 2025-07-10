import hashlib
import bisect

class ConsistentHash:
    def __init__(self, replicas=3, slots=512):
        self.replicas = replicas
        self.slots = slots
        self.ring = dict()
        self.sorted_keys = []
        self.servers = set()

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % self.slots

    def add_server(self, server):
        self.servers.add(server)
        for i in range(self.replicas):
            virtual_node = f"{server}-VN{i}"
            key = self._hash(virtual_node)
            self.ring[key] = server
            bisect.insort(self.sorted_keys, key)

    def remove_server(self, server):
        self.servers.discard(server)
        to_remove = [key for key in self.ring if self.ring[key] == server]
        for key in to_remove:
            self.ring.pop(key)
            self.sorted_keys.remove(key)

    def get_server(self, request_key):
        hash_val = self._hash(request_key)
        idx = bisect.bisect_right(self.sorted_keys, hash_val) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
