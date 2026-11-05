# 🤖 AirSense: Dual-AI Collaboration Guide (Cursor + Kiro)

> **Goal**: Complete AirSense Phases 5–10 with **zero conflicts, zero code regressions, and 100% viva readiness**.

---

## 1. The Division of Labor

```
                                  ┌───────────────────────────┐
                                  │   AirSense Architecture   │
                                  │ (AirSense_Project_Status) │
                                  └─────────────┬─────────────┘
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     ▼                                                     ▼
      ╔═════════════════════════════╗                       ╔═════════════════════════════╗
      ║            KIRO             ║                       ║           CURSOR            ║
      ║  (Chief Architect & QA)     ║                       ║ (Lead Implementation Eng.)  ║
      ╠═════════════════════════════╣                       ╠═════════════════════════════╣
      ║ • Reads `.kiro/steering/`   ║                       ║ • Reads `.cursorrules`      ║
      ║ • Writes specs & tests      ║ ─── Passes Spec ────► ║ • Modifies code files       ║
      ║ • Audits code changes       ║ ◄── Passes Code ───── ║ • Runs terminal commands    ║
      ║ • Verifies zero regressions ║                       ║ • Patches bugs & stacktraces║
      ╚═════════════════════════════╝                       ╚═════════════════════════════╝
```

### Tool Specialization:
| Task | Assigned AI | Why This Tool? |
|---|---|---|
| **Feature Specification & Acceptance Criteria** | **Kiro** (Spec Mode) | Kiro excels at converting high-level ideas into structured task lists without touching working code. |
| **Writing Unit Tests (`tests/*.py`)** | **Kiro** (Test Mode) | Ensures tests are written objectively before or during implementation. |
| **Writing Code & Modifying Files** | **Cursor** (Agent Mode) | Cursor is the fastest multi-file editor with seamless terminal and dependency handling. |
| **Fixing Bugs & Stacktraces** | **Cursor** (Agent / Chat) | Cursor can read tracebacks, jump directly to line numbers, and apply surgical edits. |
| **Reviewing Diffs & Security / Port Audits** | **Kiro** (Review Mode) | Checks that ports (5433, 9092, 11434) and schema rules weren't violated. |
| **Git Backups & Master Blueprint** | **Antigravity** (Or 1-Click Script) | Keeps the single source of truth updated and provides 1-click GitHub push. |

---

## 2. The 3-Step "Ping-Pong" Workflow (For Every Task)

### Step 1: In KIRO (Create the Spec & Test)
1. Open **Kiro IDE**.
2. Select **Spec** or start a chat in Kiro.
3. **Copy-paste this prompt**:
   > *"I am working on AirSense Phase 5, Task 5.1 (Hybrid WAQI + Open-Meteo Ingestion). Read `.kiro/steering/` and `.kiro/specs/phase5_realtime_data_integrity.md`. Please write unit tests in `airsense/tests/test_hybrid_fetch.py` that mock WAQI downtime and verify Open-Meteo fallback."*
4. Kiro creates the test file.

### Step 2: In CURSOR (Implement the Code)
1. Open **Cursor IDE** (make sure workspace is `capstone_project` on `master`).
2. Open Cursor Agent (`Ctrl + I` or Chat).
3. **Copy-paste this prompt**:
   > *"Read `.cursorrules` and `.kiro/specs/phase5_realtime_data_integrity.md`. Implement Task 5.1 in `airsense/ingestion/fetch_aqi.py`. Add the Open-Meteo fallback when WAQI is older than 2 hours or offline. Run `python -m pytest tests/` and verify all tests pass."*
4. Cursor makes the edits and verifies in terminal.

### Step 3: In KIRO (Verify & Approve)
1. Switch back to **Kiro IDE**.
2. **Copy-paste this prompt**:
   > *"Review the git diff of `airsense/ingestion/fetch_aqi.py`. Check for any breaking changes against Phases 1-4 and run `python -m pytest tests/`. If all pass, confirm the task is complete."*
3. Done! Run `airsense\scripts\github_push.bat` to push to GitHub.

---

## 3. Explaining Your Screenshots

### In Screenshot 1 (Kiro IDE):
- **Why did `airsense_cursor`, `airsense-web`, and `Air-Sense-Master.zip` show up in Kiro's explorer?**
  They showed up because Kiro was opened before we deleted them with Git, or the editor tree had not refreshed yet.
- **How to fix in Kiro**:
  1. Close the open tab `04_YOUR_TASKS.md` (which was inside the deleted `airsense_cursor` folder).
  2. Right-click anywhere in Kiro's Explorer and click **"Refresh Explorer"** (or restart Kiro).
  3. All those deleted folders will disappear, leaving only clean `airsense/`.

### In Screenshot 2 (Cursor IDE):
- **Cursor is already opened on `capstone_project` on `master` branch!**
  Notice under "Repositories", there is a leftover bookmark named `airsense_cursor`. That was just a past folder bookmark from earlier; your active working repo is `capstone_project` (checked out on `master`).
- Cursor will automatically read `.cursorrules` as soon as you type any message.

---

## 4. Emergency Golden Rule: If ANY AI Breaks Anything

If Cursor or Kiro ever makes an error, modifies the wrong file, or tests fail:
**DO NOT PANIC.** Run this single command in PowerShell:
```powershell
git reset --hard HEAD
```
Your codebase will instantly return to the 100% working baseline (32/32 tests passing) in 1 second.

