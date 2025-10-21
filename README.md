# 🧠 Jules Task Manager

A medium-level demo project to use Jules (Google's asynchronous AI coding agent) with GitHub.

## ✨ Features
- Add and manage local tasks
- Create Jules tasks (GitHub Issues with label `jules`)
- Jules automatically works on these tasks and opens Pull Requests
- Simple UI built with Streamlit + FastAPI backend

## 🛠️ Tech Stack
- Python 3.10+
- Streamlit (Frontend)
- FastAPI (Backend)
- GitHub Issues & PR
- Jules (AI agent)

## 🚀 Run Locally

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy .env.example and set your GitHub Token and Repo
cp .env.example .env

# 4. Run backend
uvicorn backend.main:app --reload --port 8000

# 5. Run Streamlit
streamlit run app/app.py
