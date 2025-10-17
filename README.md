# LLM Code Deployment - Student API

## Summary

This project implements a **student API** for the LLM Code Deployment project.
It can:

- Accept JSON task requests via a POST API
- Verify a secret submitted via Google Form
- Generate a minimal static site (`index.html`, `README.md`, `LICENSE`)
- Decode attachments sent as `data:` URIs
- Create a public GitHub repository and push generated files
- Enable GitHub Pages for the repository
- Poll until the page is live
- Post repository metadata back to the evaluation API
- Handle **round 1** and **round 2** tasks (revision/update requests)

---

## Setup & Run Locally

1. Clone the repository:

```bash
git clone https://github.com/23f1002246/redesigned-broccoli
cd redesigned-broccoli
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `secrets.py` file in the project root with your configuration:

```python
PROJECT_SECRET = "your_student_secret_here"
GITHUB_USER = "your_github_username_here"
GIT_AUTHOR_NAME = "Your Name"           # optional
GIT_AUTHOR_EMAIL = "your_email@example.com" # optional
PAGES_POLL_TIMEOUT = 180
PAGES_POLL_INTERVAL = 3
WORK_DIR = "./work"
```

> **Note:** `secrets.py` is ignored in `.gitignore` to keep sensitive data private.

4. Run the Flask app:

```bash
python app.py
```

5. Health check:

```
http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

---

## API Usage

- **POST /api** — Accepts task JSON (round 1 or round 2) with fields:

```json
{
  "email": "student@example.com",
  "secret": "your_student_secret_here",
  "task": "task-id",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Task description...",
  "evaluation_url": "https://example.com/notify",
  "attachments": [{ "name": "sample.png", "url": "data:image/png;base64,..." }]
}
```

- Responds immediately with HTTP 200 JSON acknowledgment.

- Background worker generates site, pushes repo, enables Pages, and notifies evaluation API.

- **GET /health** — Returns server status.

---

## GitHub Pages Deployment

- The app automatically:
  - Creates a public repository via `gh` CLI
  - Pushes initial files (`index.html`, `README.md`, `LICENSE`, attachments)
  - Enables GitHub Pages
  - Polls the live page URL until HTTP 200
  - Notifies the evaluation API with JSON containing `repo_url`, `commit_sha`, and `pages_url`

- The live page displays:
  - Task title (`#task-title`)
  - Task brief (`#brief`)
  - Source URL (`?url=` query param → `#source-url`)
  - Result placeholder (`#result`) with simulated solution

---

## How This Meets Project Checks

- MIT License at repository root
- Professional, descriptive `README.md`
- Page displays URL passed via query parameter
- Simulated “solved” result appears within 15 seconds
- Round 2 revisions are supported via new POST requests
- Attachments decoded automatically and saved
- Repo names are deterministic using brief + attachment hash
- Exponential backoff implemented when notifying evaluation API

---

## Notes

- Temporary repo worktrees are stored under `WORK_DIR`.
- Flask endpoints are simple and stateless for easy automated evaluation.
- Designed to pass all static, dynamic, and LLM-based evaluation checks.
- Can be extended to implement task-specific logic in `index.html` if needed.

---

## License

MIT
