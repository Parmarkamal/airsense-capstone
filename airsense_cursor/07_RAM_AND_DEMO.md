# AirSense — RAM Budget & Demo Day

Tuned for **Acer Nitro V15 — 16 GB RAM, RTX 2050, Windows 11**.

---

## RAM budget (typical running state)

| Service | RAM | Notes |
|---------|-----|-------|
| Windows 11 | ~4 GB | Baseline |
| ZooKeeper | ~256 MB | Keep default |
| Kafka | ~512 MB | Set `KAFKA_HEAP_OPTS=-Xmx512m -Xms512m` |
| TimescaleDB (Docker) | ~512 MB | Limit in `docker-compose.yml` |
| Python consumer | ~150 MB | Single process |
| Streamlit | ~300 MB | |
| Ollama phi3:mini | ~2.5 GB VRAM | GPU, not system RAM |
| ChromaDB + embeddings | ~400 MB | After index built |
| **Headroom** | ~2 GB | For browser + Power BI |

**Rule:** Do not run Grafana, MLflow UI, and Streamlit simultaneously during demo unless you've tested memory.

---

## `.wslconfig` (mandatory)

```ini
[wsl2]
memory=3GB
processors=2

[experimental]
autoMemoryReclaim=gradual
```

Without this, Docker can consume 8+ GB and crash Kafka/Ollama.

After editing:

```powershell
wsl --shutdown
# Restart Docker Desktop
```

---

## What to run when (demo day)

### Minimal demo (safest — ~8 GB)

1. ZooKeeper + Kafka
2. TimescaleDB (Docker)
3. Consumer
4. Streamlit

**Skip:** Ollama during live gauge demo; show chat screenshots instead.

### Full demo (~12 GB)

1. Everything above
2. Ollama (`ollama serve`)
3. Health chat tab live

### Do NOT run simultaneously

- MLflow UI + Ollama + Streamlit + Power BI + Docker
- Close unused browser tabs

---

## `start_demo.bat` (Week 12)

Cursor will generate this at `airsense/start_demo.bat`. Planned sequence:

```batch
@echo off
echo AirSense Demo Startup

echo [1/6] TimescaleDB...
docker compose up -d timescaledb
timeout /t 10

echo [2/6] Kafka — ensure ZooKeeper + broker already running
echo       (This script does NOT start Kafka — you start it manually)

echo [3/6] Consumer...
start "" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe consumer\consumer.py"
timeout /t 5

echo [4/6] Ollama...
start "" cmd /k "ollama serve"
timeout /t 10

echo [5/6] Streamlit...
start "" cmd /k "cd /d %~dp0 && .venv\Scripts\streamlit.exe run dashboard\app.py"

echo [6/6] Health check...
.venv\Scripts\python.exe check_system.py

echo Dashboard: http://localhost:8501
pause
```

**Note:** Kafka uses your existing ZooKeeper setup — start ZooKeeper + Kafka **before** running `start_demo.bat`.

---

## Demo-day backup matrix

| Failure | Symptom | Fallback |
|---------|---------|----------|
| WAQI API down | Fetch errors, no new data | `python ingestion/fetch_aqi_replay.py` → replays 7-day CSV to Kafka |
| Ollama crash | Chat tab errors | Kill-switch ON + show `docs/screenshots/health_chat_example.png` |
| Docker down | Dashboard empty | Static screenshots + recorded `docs/airsense_demo.mp4` |
| Kafka down | Nothing flows | Pre-recorded console consumer output + video |
| Internet down | WAQI fails | Replay mode (works offline after CSV loaded) |

---

## Replay mode (Week 12)

```powershell
python ingestion/fetch_aqi_replay.py
```

Feeds `data/backup/aqi_7day_backup.csv` into Kafka at accelerated rate. Consumer + dashboard behave identically to live mode.

---

## Pre-demo checklist (print this)

```
[ ] .wslconfig exists (3 GB)
[ ] wsl --shutdown done after .wslconfig edit
[ ] Pagefile 8–16 GB
[ ] ZooKeeper running
[ ] Kafka running on 9092
[ ] docker compose up -d timescaledb
[ ] Consumer running — rows growing in aqi_readings
[ ] Streamlit at http://localhost:8501
[ ] ollama run phi3:mini "Hello" works
[ ] data/backup/aqi_7day_backup.csv exists
[ ] docs/screenshots/ populated
[ ] docs/airsense_demo.mp4 recorded
[ ] Power BI .pbix opens
[ ] start_demo.bat tested end-to-end
[ ] WAQI attribution visible in app footer
```

---

## GPU note (RTX 2050)

| Model | VRAM | Verdict |
|-------|------|---------|
| phi3:mini (Q4) | ~2.5 GB | ✅ Use this |
| LLaVA / vision | ~5–6 GB | ❌ Skip |
| Larger LLMs (7B+) | 4+ GB | ❌ Too slow / OOM |

Check GPU: Task Manager → Performance → GPU

---

*Defense answers: [08_DEFENSE_QA.md](08_DEFENSE_QA.md)*
