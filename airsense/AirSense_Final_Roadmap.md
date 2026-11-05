# 🌬️ AirSense — Final Verified Roadmap
### Real‑Time AQI Forecasting & Private GenAI Health Advisor
*Built 100% on a single laptop – no cloud, no credit card*

---

## 1. PROJECT IDENTITY & WHY THIS EXISTS

| | |
|---|---|
| **Project Name** | AirSense |
| **Tagline** | *Know the air. Protect your health.* |
| **One‑liner** | A laptop‑only system that pulls live air‑quality data every hour, predicts the next 48 hours, and gives a local, private AI health advisor that never hallucinates because it is chained to official WHO/CPCB guidelines. |
| **Domain** | Data Engineering, Data Science, Generative AI |
| **Your Machine** | Acer Nitro V15 (16 GB RAM, Windows 11, dedicated GPU) |
| **Existing Setup** | Apache Kafka with ZooKeeper already running on `localhost:9092` – we use it exactly as is |
| **Time** | 12 weeks, 7‑10 h/week |
| **Budget** | ₹0 – every single tool is free and open‑source |
| **Privacy** | 100% local – no health question ever leaves the laptop |

---

## 2. THE REAL‑WORLD PROBLEM (WHAT TO TELL YOUR TEACHER)

Air pollution kills 7 million people every year. India has 14 of the world’s 20 most polluted cities. Yet a normal person only sees a raw AQI number – they don’t know:

- What the number means for **their** specific health (asthma, child, elderly)
- Whether tomorrow morning will be safer or worse
- What simple actions they can take right now

**AirSense changes that.** It turns raw sensor data into **personalised, forward‑looking, private health advice** – entirely on a laptop, without the internet after initial data pull.

---

## 3. FULL TECHNOLOGY STACK (WITH HONEST “WHY”)

**Every tool is free, local, and runs on your machine without any subscription.**

| Layer | Tool | Why This, Not the Alternative |
|-------|------|-------------------------------|
| **Live Data** | WAQI/AQICN API (free token) | Covers 1,000+ Indian cities, official CPCB/US embassy data. Token is free and instant. |
| **Message Broker** | Apache Kafka (your existing ZooKeeper + broker) | Already running. No need to change anything. Decouples fetch from processing, makes the system production‑grade. |
| **Stream Consumer** | Python (kafka‑python or confluent‑kafka) | Reads from Kafka, validates, writes to database. No heavy framework – just a clean Python script. |
| **Data Validation** | Pydantic v2 | Fast, Pythonic, catches bad API readings before they reach the database. |
| **Time‑Series Database** | TimescaleDB (Docker, memory‑limited) | Built on PostgreSQL – hypertables give fast queries on millions of rows, continuous aggregates enable instant dashboards. |
| **ML Forecasting** | LightGBM | Installs with a single `pip install`, trains in seconds, handles missing data natively, and gives excellent accuracy on tabular time‑series. |
| **Experiment Tracking** | MLflow (local file store) | Logs every training run’s RMSE, parameters, and model file. Launch UI on demand – no server needed. |
| **RAG Knowledge Base** | ChromaDB + all‑MiniLM‑L6‑v2 embeddings | ChromaDB runs in‑process (zero extra RAM). Embedding model is 22 MB and works fully offline after first download. |
| **Local LLM** | Ollama + phi3:mini (Q4 quantised) | Uses ~2.5 GB VRAM – fits every Nitro GPU variant. GPU‑accelerated on Windows. |
| **AI Framework** | LangChain | Connects the LLM to two tools: search health guidelines (ChromaDB) and get current AQI (database). |
| **User Dashboard** | Streamlit | Python‑native; handles live gauges, forecast charts, interactive map, and chat – all in one script. |
| **Map** | Folium | 15 lines of Python to render an interactive India map with colour‑coded city AQI bubbles. |
| **BI Reporting** | Power BI Desktop (free) | Connects to TimescaleDB with a standard PostgreSQL driver; DAX measures for category classification and city ranking. |
| **Orchestration** | Windows Task Scheduler | Runs the API fetch every hour, retrains the model weekly. No extra service to install. |
| **Alerts** | Telegram Bot API | 40 lines of Python – sends phone notification when AQI spikes. Free, instant. |

---

## 4. HARDWARE REALITY & RAM BUDGET (THE BRUTAL NUMBERS)

### Your existing ZooKeeper + Kafka
Since you already run ZooKeeper, the combined memory for both JVMs is roughly **1.2–1.5 GB** (can be tuned). We will set heap limits to keep them under 1.2 GB total.

### WSL2 memory cap (NON‑NEGOTIABLE)
Docker Desktop’s WSL2 backend defaults to taking 8 GB (50% of host RAM).  
**Before you touch Docker**, create `C:\Users\YourName\.wslconfig`:
```ini
[wsl2]
memory=3GB
processors=2
[experimental]
autoMemoryReclaim=gradual
```
Run `wsl --shutdown` and restart Docker. This caps the VM at 3 GB.

### Complete RAM budget (everything running for a demo)

| Component | RAM |
|-----------|-----|
| Windows 11 + background | ~3.5 GB |
| WSL2 VM (capped) – TimescaleDB + Grafana (optional) | ≤ 3 GB |
| ZooKeeper + Kafka (both JVMs, tuned) | ~1.2 GB |
| Python (consumer + Streamlit + LangChain) | 1.5–2.5 GB |
| Ollama + phi3:mini loaded | ~1.5 GB system + ~2.5 GB VRAM |
| VS Code + Chrome (a few tabs) | 1.5–2.5 GB |
| **Peak total** | **~11.5–13.5 GB** |

You have a safe margin of 2.5–4.5 GB on a 16 GB machine.  
**Increase the Windows pagefile to 8–16 GB** as a safety net – this prevents crashes if memory spikes; it only causes temporary slowness.

---

## 5. HIGH‑LEVEL SYSTEM ARCHITECTURE (TEXT DIAGRAM)

```text
[WAQI API – Internet]  
        │  (every hour, Task Scheduler)  
        ▼  
[Apache Kafka – topic "aqi_raw"] (your existing ZooKeeper + broker)  
        │  (real‑time, continuous consumer)  
        ▼  
[Pydantic validation]  
   ├── VALID ──────────▶ [TimescaleDB hypertable "aqi_readings"]  
   └── INVALID ────────▶ [error log]  
                │  
     ┌──────────┼──────────┐  
     │          │          │  
     ▼          ▼          ▼  
[LightGBM]  [Streamlit]  [ChromaDB (WHO/CPCB PDFs)]  
(weekly)    (dashboard)        │  
     │          │        [LangChain agent]  
     ▼          │              │  
[aqi_forecasts] │              ▼  
     │          │    [Ollama phi3:mini]  
     └──────────┤              │  
                ▼              ▼  
     [Live gauges, forecast, map, chat]  
                │  
                ▼  
[Power BI Desktop – historical reports]  
[Telegram Bot – phone alerts]
```

**All connections are localhost.** The only external call is the hourly WAQI API fetch. Zero user data leaves the machine.

---

## 6. 12‑WEEK ROADMAP – PRECISE, WEEK‑BY‑WEEK

### PHASE 1 – DATA FOUNDATION (Weeks 1‑2)

**Week 1 – Live Data Flows into Kafka**  
- Register your free WAQI token at `aqicn.org/data-platform/token/`. Store it in a `.env` file (never commit).  
- Create a Kafka topic `aqi_raw` (you can use the command line).  
- Write a Python script `fetch_aqi.py` that calls the WAQI API for 7 cities, validates the HTTP response, and publishes JSON messages to `aqi_raw`.  
- Schedule this script in Windows Task Scheduler to run every hour.  
- **Checkpoint:** Open a Kafka console consumer – you see new AQI messages arriving every hour.

**Week 2 – Clean Data Accumulates in TimescaleDB**  
- Create the `.wslconfig` file as described above. Restart WSL and Docker.  
- Write a `docker-compose.yml` for TimescaleDB only (512 MB memory limit, port 5432).  
- Create the database schema: a hypertable `aqi_readings` with 1‑day chunks.  
- Write a Python Kafka consumer that:  
  * Reads from `aqi_raw`  
  * Validates every reading with Pydantic (AQI 0‑999, PM2.5 ≥ 0, timestamp not in future)  
  * Inserts valid rows into `aqi_readings`, logs invalid ones to a file  
- **Checkpoint:** Run `SELECT COUNT(*), city FROM aqi_readings GROUP BY city;` – rows grow every hour.

---

### PHASE 2 – VISUALISATION (Weeks 3‑4)

**Week 3 – First Live Dashboard**  
- Build a Streamlit app with:  
  * A city selector dropdown  
  * Colour‑coded AQI gauges (use a colourblind‑safe palette)  
  * A 24‑hour line chart of AQI for the selected city  
- Set the dashboard to auto‑refresh every 60 seconds.  
- **Checkpoint:** Open `localhost:8501` – live gauges update as new data arrives.

**Week 4 – Insights & India Map**  
- Perform exploratory analysis in a Jupyter notebook:  
  * Diurnal pattern (AQI by hour of day)  
  * Weekday vs weekend comparison  
  * Z‑score spike detection (flag unusually high readings)  
- Add a Folium interactive India map to the Streamlit app – city markers coloured by AQI.  
- Move the best 3 EDA charts to a new “Insights” tab in the dashboard.  
- **Checkpoint:** The map shows red/orange/green bubbles. Clicking a city shows its AQI.

---

### PHASE 3 – FORECASTING (Weeks 5‑6)

**Week 5 – Train the ML Model**  
- Download historical AQI data from CPCB’s open data portal or Kaggle (not from WAQI cache).  
- Engineer features: hour of day, day of week, lag features (1h, 24h, 168h), rolling means (6h, 24h).  
- Train a LightGBM regressor with **walk‑forward validation** (never random shuffle for time series).  
- Log the experiment to MLflow: parameters, RMSE, MAE, model file.  
- Save the trained model to a staging directory and write 48‑hour forecasts into a `aqi_forecasts` table.  
- **Checkpoint:** MLflow UI shows the run; RMSE is recorded (target < 30 AQI units).

**Week 6 – Forecast Appears on Dashboard**  
- On the Streamlit dashboard, add a new chart that combines:  
  * Solid line = actual AQI (last 24 hours)  
  * Dashed line = predicted AQI (next 48 hours)  
- **Checkpoint:** The chart clearly shows where AQI is heading.

---

### PHASE 4 – AI HEALTH ADVISOR (Weeks 7‑8)

**Week 7 – Build the Knowledge Base**  
- Download WHO Air Quality Guidelines 2021 PDF and CPCB NAAQS standards PDF.  
- Use LangChain’s text splitter to chunk them into 500‑token pieces with 50‑token overlap.  
- Embed all chunks with `all-MiniLM-L6-v2` (downloads once, then runs offline).  
- Store the embeddings in a persistent ChromaDB collection on disk.  
- **Checkpoint:** Write a small test query – “What is the safe PM2.5 level for asthmatics?” – and verify it returns relevant WHO paragraphs.

**Week 8 – Safe, Grounded AI Chat**  
- Build a LangChain agent with two tools:  
  * `get_current_aqi(city)` – queries TimescaleDB for the latest reading  
  * `search_guidelines(query)` – searches ChromaDB for relevant health guideline chunks  
- Connect it to Ollama (`phi3:mini`).  
- Write a strict system prompt that:  
  * Forbids giving medical diagnosis  
  * Forces every answer to cite the source document  
  * Requires a “consult a doctor” disclaimer on every response  
- **Checkpoint:** Ask “I have asthma, Delhi AQI is 180, can I jog tomorrow?” – the answer must cite WHO/CPCB, give clear guidance, and include the disclaimer.

---

### PHASE 5 – POLISH & REPORTS (Weeks 9‑10)

**Week 9 – Professional Unified App**  
- Organise the Streamlit app into tabs: Live | Trends | Forecast | Map | Health Chat | About.  
- Add a “Suspend AI Advisor” toggle (kill‑switch) that hides the chat and optionally stops Ollama to free GPU memory.  
- Add a prominent medical disclaimer banner visible on every page.  
- Run the full system end‑to‑end: fetcher → Kafka → consumer → dashboard → AI chat.  
- **Checkpoint:** The app looks polished. Kill‑switch works. Disclaimer is always visible.

**Week 10 – Power BI Executive Reports**  
- Create a continuous aggregate in TimescaleDB that computes hourly average AQI per city.  
- Connect Power BI Desktop to TimescaleDB, import the aggregate.  
- Write DAX measures:  
  * AQI Category classification (Good/Moderate/Unhealthy…)  
  * City ranking by worst AQI  
  * Week‑over‑week trend  
- Build a two‑page report: Executive Summary + City Detail.  
- **Checkpoint:** Power BI opens and displays months of data with interactive filters.

---

### PHASE 6 – AUTOMATION, ALERTS & DEMO HARDENING (Weeks 11‑12)

**Week 11 – MLOps & Phone Alerts**  
- Write a standalone Python retraining script that:  
  * Extracts the latest 4 weeks from TimescaleDB  
  * Trains a new LightGBM model  
  * Compares its RMSE with the current production model’s RMSE (stored in a JSON file)  
  * If the new model is better, copies it to the production folder and updates the JSON  
- Schedule this script in Task Scheduler to run weekly.  
- Write a Telegram bot script that:  
  * Checks the latest AQI for each city every hour  
  * If AQI exceeds a threshold (e.g., 200), sends a message to your phone  
- **Checkpoint:** Manually trigger a spike – your phone buzzes with an alert within seconds.

**Week 12 – Stress Test, Backup Plans, Defence Prep**  
- Run the entire system for 24 hours continuously. Monitor RAM and disk.  
- Prepare and test three backup scenarios:  
  * **Live API dead** – switch to replay mode (feed a 7‑day backup CSV through Kafka)  
  * **LLM hangs** – toggle kill‑switch, show pre‑generated chat screenshots  
  * **Docker containers fail** – have static dashboard screenshots and a recorded demo video ready  
- Write a complete README with architecture diagram, setup steps, and known limitations.  
- Create `start_demo.bat` – a one‑click script that launches all services in the correct order.  
- Record a 5‑minute demo video showing the full system working.  
- Rehearse the defence Q&A at least 5 times.

---

## 7. SKILLS YOU WILL ACTUALLY HAVE (MAPPED TO JOB ROLES)

| Role | Skills from AirSense |
|------|----------------------|
| **Data Engineer** | Kafka topic design, producer/consumer, Pydantic validation, TimescaleDB hypertables, Docker/WSL2, Task Scheduler orchestration |
| **Data Scientist** | Time‑series feature engineering, walk‑forward validation, LightGBM training, RMSE/MAE evaluation, EDA |
| **MLOps Engineer** | MLflow experiment tracking, champion‑challenger model promotion, automated weekly retraining |
| **AI/GenAI Engineer** | RAG architecture, ChromaDB, local LLM deployment (Ollama), LangChain agent design, safety prompt engineering |
| **Data Analyst** | Streamlit interactive dashboards, Plotly/Plotly Map, Power BI with DAX, EDA |
| **Software Engineer** | Modular project structure, unit testing, logging, RAM budgeting, Git hygiene, backup scripting |

---

## 8. DEMO DAY BACKUP STRATEGY (THREE LAYERS OF DEFENCE)

1. **Internet down / WAQI API fails** → Click the “Replay Mode” toggle. A pre‑loaded 7‑day CSV is fed through Kafka. The pipeline, dashboards, and AI advisor work identically.  
2. **Ollama/LLM crashes or runs out of memory** → Toggle the kill‑switch. The AI chat is hidden. The rest of the dashboard continues unaffected. Show 3‑4 pre‑generated example conversations.  
3. **Docker containers won’t start** → Show static screenshots of every dashboard page and the Power BI report. Play the 5‑minute recorded demo video. You can still answer all questions.

---

## 9. DEFENCE Q&A – READY ANSWERS

| Question | Answer |
|----------|--------|
| **Why Kafka for just 7 cities?** | Kafka decouples ingestion from processing. If I add 500 stations later, only the producer changes; the consumer stays the same. It also gives replay capability – if the consumer crashes, it can re‑read from the last committed offset. |
| **Why did you keep ZooKeeper?** | My Kafka installation uses the existing ZooKeeper setup, which is still fully supported in many deployments. Migrating to KRaft would add unnecessary complexity for a single‑machine capstone. |
| **How do you guarantee the AI doesn’t give dangerous health advice?** | The LLM is forced to use only the text retrieved from official WHO/CPCB documents. It cannot make up statistics. Every answer must cite its source and include a doctor disclaimer. |
| **Why LightGBM and not a deep learning model?** | LightGBM gives comparable accuracy on tabular time‑series, trains in seconds, and installs cleanly on Windows. It also provides feature importance, which I use to explain predictions. |
| **What’s your RMSE and is it good?** | The target RMSE is under 30 AQI units. More important is directional accuracy – the model correctly predicts whether AQI will rise or fall, which is what actually matters for a user planning their day. |
| **Are you legally allowed to use WAQI data?** | Yes. I use my own registered token, attribute WAQI in the app footer, and use only CPCB/Kaggle data for historical training – not long‑term WAQI caching. |
| **How does the system work without the internet?** | After the initial data pull, the LLM runs fully offline. If the live API dies, a “replay mode” feeds historical CSV data through the same pipeline. The user experience is identical. |

---

## 10. RISK ASSESSMENT & PROBABILITY OF COMPLETION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Kafka/ZooKeeper JVM memory too high | Medium | System slowdown | Set heap limits in startup scripts; already accounted in RAM budget |
| Docker WSL2 consumes too much RAM | High (if uncapped) | Crash | `.wslconfig` created in Week 0 – mandatory step |
| WAQI API rate limiting or downtime | Low | Live data stops | Replay mode with 7‑day backup CSV |
| LightGBM RMSE above target early on | Medium | Defence criticism | Document iteration; show improvement week‑over‑week in MLflow |
| LangChain version conflict | Low | Import errors | Pin exact versions in `requirements.txt` from Day 1 |
| Ollama hangs during live demo | Low | Chat unusable | Kill‑switch + pre‑generated example conversations |

**Overall probability of completing the full system as described: 90%+**  
The remaining 10% is entirely from skipping the mandatory RAM capping or ignoring the backup plans.

---

## 11. WHAT YOU CAN ADD LATER (AFTER THE CORE IS DONE)

- **Physical sensor (ESP32 + PMS5003, ~₹2,000)** – your own hyper‑local AQI station  
- **WhatsApp/Email alerts** – extend the Telegram bot to other channels  
- **Anomaly detection (Isolation Forest)** – flag unusual pollution events without manual thresholds  
- **FastAPI backend** – serve the forecast as a REST API for other apps  
- **Bilingual UI (English + Hindi/Gujarati)** – meaningful for real Indian users  
- **Docker‑compose the whole stack** – make everything launch with one command on any machine  

---

## 12. FINAL VERDICT

**AirSense, exactly as laid out in this roadmap, is the most complete, realistic, and recruiter‑ready capstone you can build on a single laptop.** It solves a massive, visible Indian problem with real‑time data, machine learning, and a private, grounded AI advisor. It covers every skill a modern data professional needs. It fits your existing Kafka setup. It fits your laptop’s RAM. And it has a bulletproof backup plan for every possible demo‑day disaster.
