---
name: start-teardown
description: Launches the Teardown full-stack application (FastAPI backend on port 8000 + Next.js frontend on port 3005) and automatically opens the app in the user's default browser. Trigger whenever the user asks to start Teardown, run Teardown, launch the app, open Teardown in browser, or start servers.
---

# Start Teardown Skill

This skill launches the complete Teardown application stack and opens `http://localhost:3005` in the user's default web browser.

## What It Does
1. Kills any leftover stale processes on ports 8000 (FastAPI) and 3005 (Next.js).
2. Launches the Python FastAPI backend (`app.main:app`) on port 8000 in background mode.
3. Launches the Next.js App Router frontend on port 3005 in dev mode.
4. Executes macOS native `open http://localhost:3005` to automatically open the web app in the user's default browser.

## Command Execution
Run the project's root launcher script:

```bash
/Users/jatinpandey/Antigravity/Frontend\ Design\ DNA\ Extractor/start.sh
```
