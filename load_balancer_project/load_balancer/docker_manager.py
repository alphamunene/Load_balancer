import os
import random
import string
import time

# Function to generate a random server name
def generate_random_name(length=6):
    return "S" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to spawn a new server container
def spawn_container(name):
    print(f"[INFO] Spawning container: {name}")
    cmd = (
        f"docker run --name {name} "
        f"--network net1 --network-alias {name} "
        f"-e SERVER_ID={name[-1]} -d server_image"
    )
    print("[DEBUG] Command:", cmd)
    result = os.popen(cmd).read().strip()
    print("[DEBUG] Result:", result)

    if result == "":
        print(f"[ERROR] Failed to start container: {name}")
        return False

    time.sleep(1)  # give the container a moment to start
    return True

# Function to remove a server container
def remove_container(name):
    print(f"[INFO] Removing container: {name}")
    stop_cmd = f"docker stop {name}"
    rm_cmd = f"docker rm {name}"

    print("[DEBUG] Stop command:", stop_cmd)
    print("[DEBUG] Remove command:", rm_cmd)

    os.system(stop_cmd)
    os.system(rm_cmd)
    time.sleep(1)

