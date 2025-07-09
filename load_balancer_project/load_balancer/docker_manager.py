import os
import random
import string
import subprocess

# Base image name for the server containers
IMAGE_NAME = "server_image"
DOCKER_NETWORK = "net1"

def generate_random_name():
    """Generates a random hostname like S8421"""
    return "S" + ''.join(random.choices(string.digits, k=4))

def spawn_container(name):
    """
    Spawns a new container with given name, attached to the Docker network.
    Returns True if container was started successfully, False otherwise.
    """
    print(f"[INFO] Spawning container: {name}")
    cmd = (
        f"docker run -d --name {name} "
        f"--network {DOCKER_NETWORK} "
        f"--network-alias {name} "
        f"-e SERVER_ID={name} "
        f"{IMAGE_NAME}"
    )
    result = os.popen(cmd).read().strip()
    if result:
        print(f"[SUCCESS] Container {name} started with ID {result}")
        return True
    else:
        print(f"[ERROR] Failed to start container {name}")
        return False

def remove_container(name):
    """
    Stops and removes a container by name.
    Returns True if successful, False otherwise.
    """
    print(f"[INFO] Removing container: {name}")
    try:
        os.system(f"docker stop {name} > /dev/null 2>&1")
        os.system(f"docker rm {name} > /dev/null 2>&1")
        print(f"[SUCCESS] Container {name} removed")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to remove container {name}: {str(e)}")
        return False

def list_running_servers():
    """
    Returns a list of running server container names.
    """
    result = subprocess.getoutput("docker ps --format '{{.Names}}'")
    return [name for name in result.splitlines() if name.startswith("server") or name.startswith("S")]
