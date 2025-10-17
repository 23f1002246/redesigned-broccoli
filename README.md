# LLM Code Deployment - Student API

## Summary

This project implements a **student API** for the LLM Code Deployment project.  
It can:

- Accept JSON task requests via a POST API
- Verify a secret submitted via Google Form
- Generate a minimal static site (HTML, README, LICENSE)
- Create a public GitHub repository and push the generated files
- Enable GitHub Pages for the repository
- Poll until the page is live
- Post back repository metadata to the evaluation API
- Handle round 1 and round 2 tasks (revision/update requests)

---

## How to Run Locally

1. Clone the repository:

```bash
git clone <your_repo_url>
cd llm-deployer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (or create a `.env` file):

```bash
export PROJECT_SECRET=your_student_secret_here
export GITHUB_USER=your_github_username_here
export GIT_AUTHOR_NAME="Your Name"
export GIT_AUTHOR_EMAIL="your_email@example.com"
export PAGES_POLL_TIMEOUT=180
export PAGES_POLL_INTERVAL=3
```

4. Run the app:

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

## GitHub Pages Deployment

- The app automatically creates a public repository using `gh` CLI.
- Pushes initial files and enables GitHub Pages.
- The live page URL is returned to the evaluation API in JSON format.
- The page displays:
  - Task title
  - Task brief
  - Source URL (from `?url=` query param)
  - Result placeholder (`#result`) with simulated solution

---

## How This Meets Project Checks

- MIT License at repository root
- README.md is professional and descriptive
- Static page displays URL passed via query param
- Simulated “solved” result appears within 15 seconds
- Supports round 2 revisions by receiving new POST JSON

---

## Notes

- Attachments sent via `data:` URI in task JSON are automatically decoded and saved.
- The repo is named using a safe hash based on the task brief and attachments.
- Exponential backoff is implemented when notifying the evaluation API.
- Flask endpoints:
  - `POST /api` — Accepts task JSON
  - `GET /health` — Returns server status

---

## License

MIT
