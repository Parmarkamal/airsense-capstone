# AirSense — Your Tasks (Manual)

These tasks **cannot be automated** by Cursor. You must do them on your machine.

---

## Week 0 — Before any code runs

### Kafka (existing setup)

- [ ] Start ZooKeeper, then Kafka broker
- [ ] Confirm broker reachable: `localhost:9092`
- [ ] Note your Kafka install path (e.g. `C:\kafka`)

**Do not migrate to KRaft.** Use your current ZooKeeper + Kafka setup.

### WSL / Docker RAM limit

Create `C:\Users\<YourName>\.wslconfig`:

```ini
[wsl2]
memory=3GB
processors=2

[experimental]
autoMemoryReclaim=gradual
```

Then:

```powershell
wsl --shutdown
# Restart Docker Desktop
```

### Prerequisites verification

| Tool | Check command | Required by |
|------|---------------|-------------|
| Java 17 | `java -version` | Kafka |
| Python 3.10+ | `python --version` | All scripts |
| Docker Desktop | `docker --version` | Week 2 |
| Git | `git --version` | Version control |
| Ollama | `ollama --version` | Week 8 |
| Power BI Desktop | Installed | Week 10 |

### WAQI token

1. Go to https://aqicn.org/data-platform/token/
2. Register → copy token
3. Copy `airsense/.env.example` → `airsense/.env`
4. Set `WAQI_TOKEN=your_real_token`

### Ollama model (before Week 8)

```powershell
ollama pull phi3:mini
ollama run phi3:mini "What is PM2.5?"
```

### Windows pagefile

System Properties → Advanced → Performance → Virtual Memory → Custom: **8192–16384 MB**

---

## Week 1 — Kafka topic + scheduling

### Create topic (one time)

```powershell
cd C:\kafka
bin\windows\kafka-topics.bat --create `
  --topic aqi_raw `
  --bootstrap-server localhost:9092 `
  --partitions 1 `
  --replication-factor 1
```

If topic exists, you'll see an error — that's fine.

### Install Python dependencies

```powershell
cd c:\STUDY\MSC_BI_Analytics\sem_03\capstone_project\airsense
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run and verify

```powershell
python scripts/test_waqi_kafka.py
python ingestion/fetch_aqi.py
```

### Task Scheduler (hourly fetch)

- **Program:** `C:\...\airsense\.venv\Scripts\python.exe`
- **Arguments:** `C:\...\airsense\ingestion\fetch_aqi.py`
- **Trigger:** Daily, repeat every 1 hour
- **Condition:** Start only if network available

---

## Week 2 — Docker TimescaleDB

```powershell
cd airsense
docker compose up -d timescaledb
```

Apply SQL:

```powershell
docker exec -i airsense-timescaledb psql -U airsense -d airsense_db < sql/001_create_hypertable.sql
```

Run consumer in a separate terminal:

```powershell
python consumer/consumer.py
```

---

## Week 5 — Historical data

Download **before** ML training (not from WAQI cache):

- CPCB open data: https://data.gov.in/
- Kaggle Indian AQI datasets

Save CSV to: `airsense/data/historical/`

---

## Week 7 — WHO/CPCB PDFs

Download and save to `airsense/data/docs/`:

- WHO Air Quality Guidelines 2021 (PDF)
- CPCB NAAQS / AQI guidance (PDF)

---

## Week 10 — Power BI

Build 2-page report in Power BI Desktop connected to:

- Host: `localhost`
- Port: `5432`
- Database: `airsense_db`
- User/password from `.env`

---

## Week 11 — Telegram bot

1. Message `@BotFather` → `/newbot` → save token
2. Add to `.env`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. Get chat ID via helper script (Cursor provides in Week 11)

---

## Week 12 — Demo assets

- [ ] Record 5-minute demo video → `docs/airsense_demo.mp4`
- [ ] Screenshots → `docs/screenshots/`
- [ ] Rehearse viva using [08_DEFENSE_QA.md](08_DEFENSE_QA.md)
- [ ] Run 24h stress test (Kafka + consumer + fetch scheduled)

---

## Ongoing — every week

- [ ] Keep ZooKeeper + Kafka running during development
- [ ] Hit the week's checkpoint before asking Cursor for the next week
- [ ] Report errors with full terminal output (Cursor fixes in Agent mode)

---

*What Cursor builds: [05_AI_TASKS.md](05_AI_TASKS.md)*
