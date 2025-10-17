"""
app.py — Vercel-Compatible Flask API for LLM Code Deployment

Modes:
- LOCAL_MODE=true → full local pipeline using git + gh CLI (calls app_local_pipeline.py)
- LOCAL_MODE=false → safe mock mode for Vercel (no subprocesses, no filesystem writes)

Features:
- Accepts POST JSON tasks
- Verifies secret via secrets.py
- Simulates or runs repo creation + GitHub Pages enablement
- Notifies evaluation API with repo metadata
"""

import os
import time
import logging
import requests
from flask import Flask, request, jsonify
from threading import Thread

# --- Import configuration from secrets.py ---
from secrets import (
    PROJECT_SECRET,
    GITHUB_USER,
    GIT_AUTHOR_NAME,
    GIT_AUTHOR_EMAIL,
    PAGES_POLL_TIMEOUT,
    PAGES_POLL_INTERVAL,
    WORK_DIR,
)

# --- Flask setup ---
app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("vercel-app")

# Mode control
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"


# --- Helper: Simulated Repo Creation for Vercel ---
def fake_create_repo(task, brief, attachments):
    """Simulate GitHub repo + pages URL creation (for Vercel runtime)."""
    repo_name = f"mock-{task.replace(' ', '-')}"
    logger.info(f"[Vercel] Simulating repo creation: {repo_name}")
    repo_url = f"https://github.com/{GITHUB_USER}/{repo_name}"
    pages_url = f"https://{GITHUB_USER}.github.io/{repo_name}/"
    return repo_url, pages_url


# --- Helper: Notify evaluation server with retries ---
def notify_evaluation(evaluation_url: str, payload: dict, max_attempts: int = 6):
    logger.info(f"Notifying evaluation server at {evaluation_url}")
    headers = {"Content-Type": "application/json"}

    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(
                evaluation_url, json=payload, headers=headers, timeout=10
            )
            if resp.status_code == 200:
                logger.info(f"✅ Evaluation notified successfully (attempt {attempt})")
                return True
            else:
                logger.warning(f"⚠️ Attempt {attempt}: Received {resp.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt} failed: {e}")
        time.sleep(2**attempt)
    logger.error("❌ All retries failed notifying evaluation server.")
    return False


# --- Flask Endpoints ---


@app.route("/api", methods=["POST"])
def api_handler():
    """Main API endpoint for accepting LLM deployment tasks."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid json"}), 400

    # Basic validation
    if data.get("secret") != PROJECT_SECRET:
        logger.warning("Invalid secret received.")
        return jsonify({"error": "invalid secret"}), 400

    task = data.get("task", "untitled")
    brief = data.get("brief", "")
    evaluation_url = data.get("evaluation_url", "")
    attachments = data.get("attachments", [])
    round_idx = int(data.get("round", 1))

    ack = {"status": "ok", "task": task, "round": round_idx}
    logger.info(
        f"Accepted task '{task}' (round {round_idx}) — mode={'local' if LOCAL_MODE else 'vercel'}"
    )

    if LOCAL_MODE:
        # Local mode → use real git + gh pipeline
        Thread(target=_do_pipeline_local, args=(data,), daemon=True).start()
    else:
        # Vercel mode → simulate repo + page creation
        repo_url, pages_url = fake_create_repo(task, brief, attachments)
        payload = {
            "email": data.get("email"),
            "task": task,
            "round": round_idx,
            "nonce": data.get("nonce"),
            "repo_url": repo_url,
            "commit_sha": "mock-sha123",
            "pages_url": pages_url,
        }
        notify_evaluation(evaluation_url, payload)

    return jsonify(ack), 200


def _do_pipeline_local(data: dict):
    """
    Local-only pipeline runner.
    This dynamically imports app_local_pipeline.py to avoid loading subprocess
    logic in Vercel mode.
    """
    try:
        from app_local_pipeline import run_local_pipeline

        run_local_pipeline(data)
    except ImportError as e:
        logger.error("Missing app_local_pipeline.py: %s", e)
    except Exception as e:
        logger.exception("Error running local pipeline: %s", e)


@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return (
        jsonify(
            {
                "status": "ok",
                "mode": "local" if LOCAL_MODE else "vercel",
                "github_user": GITHUB_USER,
            }
        ),
        200,
    )


# --- Entrypoint ---
if __name__ == "__main__":
    if PROJECT_SECRET is None or GITHUB_USER is None:
        logger.error("Missing PROJECT_SECRET or GITHUB_USER in secrets.py")
        raise SystemExit(1)

    logger.info(f"Starting Flask server (mode={'local' if LOCAL_MODE else 'vercel'})")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
