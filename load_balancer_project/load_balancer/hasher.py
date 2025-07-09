my hashing import bisect

class ConsistentHashRing:
    def __init__(self, num_slots=512, virtual_nodes_per_server=9):
        self.num_slots = num_slots
        self.virtual_nodes_per_server = virtual_nodes_per_server
        self.ring = []
        self.server_map = {}

    def _hash_server(self, server_id, vnode_id):
        return (server_id + 3 * vnode_id + 25) % self.num_slots

    def _hash_request(self, request_id):
        return (3 * request_id + 289) % self.num_slots

    def add_server(self, server_id):
        for vnode_id in range(self.virtual_nodes_per_server):
            pos = self._hash_server(server_id, vnode_id)
            while pos in self.server_map:
                vnode_id += 1
                pos = (self._hash_server(server_id, vnode_id) + vnode_id * vnode_id) % self.num_slots
            self.ring.append(pos)
            self.server_map[pos] = server_id
        self.ring.sort()

    def remove_server(self, server_id):
        to_remove = [pos for pos, sid in self.server_map.items() if sid == server_id]
        for pos in to_remove:
            self.ring.remove(pos)
            del self.server_map[pos]

    def get_server(self, request_id):
        if not self.ring:
            return None
        request_hash = self._hash_request(request_id)
        idx = bisect.bisect_right(self.ring, request_hash)
        if idx == len(self.ring):
            idx = 0
        return self.server_map[self.ring[idx]]import bisect

class ConsistentHashRing:
    def __init__(self, num_slots=512, virtual_nodes_per_server=9):
        self.num_slots = num_slots
        self.virtual_nodes_per_server = virtual_nodes_per_server
        self.ring = []
        self.server_map = {}        # position → server_id
        self.id_to_name = {}        # server_id → name

    def _hash_server(self, server_id, vnode_id):
        return (server_id + 3 * vnode_id + 25) % self.num_slots

    def _hash_request(self, request_id):
        return (3 * request_id + 289) % self.num_slots

    def add_server(self, server_id, name):
        self.id_to_name[server_id] = name
        for vnode_id in range(self.virtual_nodes_per_server):
            pos = self._hash_server(server_id, vnode_id)
            while pos in self.server_map:
                vnode_id += 1
                pos = (self._hash_server(server_id, vnode_id) + vnode_id * vnode_id) % self.num_slots
            self.ring.append(pos)
            self.server_map[pos] = server_id
        self.ring.sort()

    def remove_server(self, server_id):
        to_remove = [pos for pos, sid in self.server_map.items() if sid == server_id]
        for pos in to_remove:
            self.ring.remove(pos)
            del self.server_map[pos]
        if server_id in self.id_to_name:
            del self.id_to_name[server_id]

    def get_server(self, request_id):
        if not self.ring:
            return None
        request_hash = self._hash_request(request_id)
        idx = bisect.bisect_right(self.ring, request_hash)
        if idx == len(self.ring):
            idx = 0
        sid = self.server_map[self.ring[idx]]
        return self.id_to_name.get(sid, None)  # returns name like "server1" or "S4"
