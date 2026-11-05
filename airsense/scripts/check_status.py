import socket
import urllib.request
import json
import subprocess
import sys

def check_port(host, port):
    try:
        s = socket.create_connection((host, port), timeout=2.0)
        s.close()
        return True
    except Exception:
        return False

def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", headers={"User-Agent": "AirSense"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except Exception as e:
        return False, str(e)

def check_docker():
    try:
        res = subprocess.run(["docker", "ps", "--format", "{{.Names}} ({{.Status}})"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
            return True, lines
        return False, res.stderr.strip()
    except Exception as e:
        return False, str(e)

print("=" * 60)
print("AirSense End-to-End System Readiness Check")
print("=" * 60)

docker_up, docker_info = check_docker()
print(f"Docker Daemon    : {'ONLINE' if docker_up else 'OFFLINE'}")
if docker_up:
    print(f"  Active Containers: {docker_info if docker_info else 'None running'}")
else:
    print(f"  Detail: {docker_info}")

kafka_up = check_port("localhost", 9092)
print(f"Kafka (Port 9092): {'ONLINE' if kafka_up else 'OFFLINE'}")

tsdb_up = check_port("localhost", 5433)
print(f"TimescaleDB (5433): {'ONLINE' if tsdb_up else 'OFFLINE'}")

ollama_up, models = check_ollama()
print(f"Ollama (Port 11434): {'ONLINE' if ollama_up else 'OFFLINE'}")
if ollama_up:
    print(f"  Models: {models}")

st_up = check_port("localhost", 8501)
print(f"Streamlit (8501) : {'ONLINE' if st_up else 'OFFLINE'}")

print("=" * 60)

