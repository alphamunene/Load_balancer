import os
import random
import string

def generate_random_name(prefix='S'):
    return prefix + ''.join(random.choices(string.digits, k=3))

def spawn_container(name):
    command = (
        f"docker run -d --rm --network net1 --network-alias {name} "
        f"-e SERVER_ID={name} --name {name} loadbalancer-server"
    )
    return os.popen(command).read().strip()

def remove_container(name):
    os.system(f"docker stop {name}")