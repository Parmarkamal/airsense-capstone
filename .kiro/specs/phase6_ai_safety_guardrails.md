# Specification: Phase 6 — AI Safety & Domain Guardrails

## 1. Objective
Transform the GenAI Health Advisor into a safe, grounded, defensible medical intelligence system by implementing out-of-domain refusal, mandatory medical disclaimers, confidence thresholding, and 4 specialized user persona quick-pills.

## 2. Target Files
- `airsense/rag/health_advisor.py`: Guardrail classification, refusal logic, disclaimer injection.
- `airsense/dashboard/components/chat_view.py`: Persona pill buttons (🏃 Athlete, 👶 Parent, 🫁 Asthma/Elderly, 🚴 Commuter).
- `airsense/tests/test_rag.py`: New unit tests verifying out-of-domain rejection and disclaimer presence.

## 3. Tasks

### Task 6.1: Domain Classifier & Polite Refusal
- Function: `is_air_quality_or_health_query(query: str) -> bool`
- Check keywords and intent. If the query asks for stock trading, general programming, movie recommendations, or medical prescriptions outside air quality/respiratory health:
  - Do NOT query Ollama.
  - Return: *"I am the AirSense AI Health Advisor, specialized in urban air quality and respiratory health impacts. I can only answer questions related to air pollution, AQI readings, WHO/CPCB standards, and outdoor activity precautions. Please ask an air quality or health-related question."*

### Task 6.2: Grounding & Mandatory Medical Disclaimer
- Append a standard disclaimer to every generated response:
  - *"⚠️ **Medical Disclaimer**: AirSense provides general health advisories based on official WHO (2021) and CPCB NAAQS guidelines and live air quality data. This is not medical diagnosis or prescription. Consult a physician for acute respiratory or cardiovascular symptoms."*

### Task 6.3: RAG Confidence Thresholding
- If vector retrieval distance > 0.45 (or retrieved chunks are empty):
  - Do not let the LLM extrapolate or hallucinate.
  - Inject a verified static fallback response from `knowledge_documents.py` for the current city's AQI category.

### Task 6.4: Persona Quick-Pills
- In `dashboard/components/chat_view.py`, display 4 one-click buttons above chat input:
  1. 🏃 **Morning Runner**: "Is it safe to run outside in {city} this morning?"
  2. 👶 **Parent with Toddler**: "Can my toddler play in the park in {city} today?"
  3. 🫁 **Asthma Patient**: "What precautions should asthma patients take at current AQI in {city}?"
  4. 🚴 **Daily Commuter**: "Should I wear an N95 mask during my commute in {city} today?"

## 4. Acceptance Criteria
- [ ] Asking "How do I write a Python quicksort?" returns the polite refusal without calling LLM.
- [ ] Every valid response includes the medical disclaimer.
- [ ] Persona buttons auto-populate chat input and return grounded answers.
- [ ] All tests pass: `python -m pytest tests/test_rag.py`.

