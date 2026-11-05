# Code Rules, Quality Standards & Viva Safety

## 1. Single Source of Truth
- The master progress tracker, viva questions, and architecture decisions reside in `AirSense_Project_Status.md`.
- Never create arbitrary loose `.md` files in the root directory. Keep specifications inside `.kiro/specs/`.

## 2. Code Quality & Standards
- **Python**: Python 3.11 with strict type annotations (`typing`, `from __future__ import annotations`).
- **Validation**: Pydantic v2 models in `consumer/validate.py`. Any new fields must have defaults or allow `None`.
- **Database**: TimescaleDB on host `localhost`, port `5433`. Never commit hardcoded connection strings outside `config.yaml` / `.env`.
- **Zero Cloud Cost**: All components (Kafka, TimescaleDB, Ollama `llama3.2:3b`, LightGBM, Streamlit) must run 100% locally on a Windows laptop without requiring paid cloud APIs.

## 3. Disaster Recovery Protocol
- If any code edit breaks the project or causes tests to fail:
  ```powershell
  git status
  git reset --hard HEAD
  ```
- This restores the project instantly to the last verified commit.
