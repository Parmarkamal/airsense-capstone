# AirSense — Setup Prerequisites

Complete **before Week 1 code runs**. Order matters.

---

## 1. Java 17 (Kafka)

Kafka requires Java. Verify:

```powershell
java -version
```

Expected: `openjdk version "17.x"` or similar.

Download if missing: https://adoptium.net/

---

## 2. Python 3.10+

```powershell
python --version
```

Create virtual environment in project:

```powershell
cd c:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Apache Kafka (ZooKeeper mode — keep existing)

**Decision:** Use your **existing ZooKeeper + Kafka** on `localhost:9092`. Do **not** migrate to KRaft.

### Startup order

1. Start ZooKeeper
2. Start Kafka broker
3. Verify port 9092 is listening

### Typical paths (adjust to your install)

```powershell
# Terminal 1 — ZooKeeper
cd C:\kafka
bin\windows\zookeeper-server-start.bat config\zookeeper.properties

# Terminal 2 — Kafka
cd C:\kafka
set KAFKA_HEAP_OPTS=-Xmx512m -Xms512m
bin\windows\kafka-server-start.bat config\server.properties
```

### Memory tip

Limit Kafka heap to 512 MB on 16 GB laptop:

```powershell
set KAFKA_HEAP_OPTS=-Xmx512m -Xms512m
```

---

## 4. Docker Desktop + WSL2

### Create `.wslconfig` FIRST

File: `C:\Users\<YourName>\.wslconfig`

```ini
[wsl2]
memory=3GB
processors=2

[experimental]
autoMemoryReclaim=gradual
```

Apply:

```powershell
wsl --shutdown
# Restart Docker Desktop from system tray
```

Verify:

```powershell
docker --version
docker run hello-world
```

---

## 5. WAQI API token

1. Visit https://aqicn.org/data-platform/token/
2. Register with email
3. Copy token immediately
4. Add to `airsense/.env`:

```env
WAQI_TOKEN=your_token_here
```

**Free tier:** ~1,000 requests/day. AirSense uses 6 cities × 24 hours = 144/day — well within limit.

---

## 6. Git

```powershell
git --version
```

Ensure `.env` is never committed (already in `.gitignore`).

---

## 7. Ollama (Week 0 install, Week 8 use)

Download: https://ollama.com

```powershell
ollama --version
ollama pull phi3:mini
ollama run phi3:mini "What is PM2.5?"
```

**Model size:** ~2.3 GB. Use **phi3:mini only** — no vision models on RTX 2050.

Ollama serves on `http://localhost:11434` by default.

---

## 8. Power BI Desktop (Week 10)

Download free edition: https://powerbi.microsoft.com/desktop/

No license needed for local `.pbix` files.

---

## 9. Optional downloads (later weeks)

| Item | When | Location |
|------|------|----------|
| WHO Air Quality Guidelines 2021 PDF | Before Week 7 | `data/docs/` |
| CPCB NAAQS PDF | Before Week 7 | `data/docs/` |
| CPCB/Kaggle historical CSV | Before Week 5 | `data/historical/` |
| Telegram bot token | Week 11 | `.env` |

---

## 10. Windows pagefile

Prevents OOM during Docker + Ollama + Streamlit overlap:

1. System Properties → Advanced → Performance Settings
2. Advanced → Virtual Memory → Change
3. Custom size: **Initial 8192 MB**, **Maximum 16384 MB**
4. Restart if prompted

---

## Environment file template

Copy and fill:

```powershell
copy .env.example .env
notepad .env
```

Required for Week 1:

- `WAQI_TOKEN`
- `KAFKA_BOOTSTRAP_SERVERS` (default `localhost:9092`)

Required for Week 2+:

- `POSTGRES_*` variables

---

## Verification script (Week 1)

After setup:

```powershell
cd airsense
.venv\Scripts\activate
python scripts/test_waqi_kafka.py
```

Expected output:

```
[OK] WAQI token valid — sample AQI for ahmedabad: ...
[OK] Kafka broker reachable at localhost:9092
[OK] Test message published to topic 'aqi_raw'
```

---

*RAM budget & demo: [07_RAM_AND_DEMO.md](07_RAM_AND_DEMO.md)*
