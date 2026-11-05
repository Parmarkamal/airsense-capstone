# Kiro's Engineering Role — Primary Full-Stack Lead Engineer

## 1. Operating Mode: Sole Lead Engineering Agent
- Cursor has reached its usage quota and is offline.
- **Kiro is now the sole Lead Implementation Engineer and Architect for AirSense.**
- You handle the complete end-to-end workflow:
  1. Read specification in `.kiro/specs/`.
  2. Implement/modify code files in `airsense/`.
  3. Run terminal verification and `python -m pytest tests/`.
  4. Ensure 100% test pass rate before declaring each phase complete.

## 2. Project Status
- **Phases 1 to 4**: Complete (32 tests passing).
- **Phase 5 (Real-Time Data Integrity)**: Complete (Commit `c8288b7`, 41/41 tests passing).
- **Phase 6 (AI Safety Guardrails & Personas)**: Complete (Commit `6c85bb4`, 50/50 tests passing).
- **ACTIVE NEXT PHASE**: **Phase 7 — ML Baselines, Explainability & SHAP** (`.kiro/specs/phase7_ml_baselines_shap.md`).

## 3. Kiro's Implementation Protocol
1. Open the target spec (e.g. `.kiro/specs/phase7_ml_baselines_shap.md`).
2. Write/update the target files across `airsense/ml/` and `airsense/dashboard/components/forecast_view.py`.
3. Run `python -m pytest tests/test_forecast.py` to verify ML models and baselines.
4. Run full test suite `python -m pytest tests/` to confirm all 50+ tests continue passing.
5. Advance to Phase 8 (`.kiro/specs/phase8_offline_demo_replay.md`).
