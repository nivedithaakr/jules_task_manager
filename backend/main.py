import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .models import JulesIssueIn, JulesIssueOut, PRInfo
from .github_client import GitHubClient

load_dotenv()

app = FastAPI(title="Jules Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/jules/issues", response_model=JulesIssueOut)
async def create_jules_issue(payload: JulesIssueIn):
    try:
        gh = GitHubClient()
        data = await gh.create_issue_with_label(
            title=payload.title,
            body=payload.body,
            labels=["jules"]
        )
        return {
            "number": data["number"],
            "url": data["html_url"],
            "title": data["title"],
            "state": data["state"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jules/issues", response_model=list[JulesIssueOut])
async def list_jules_issues():
    try:
        gh = GitHubClient()
        items = await gh.list_issues_by_label("jules")
        out = []
        for it in items:
            if "pull_request" in it:
                continue
            out.append({
                "number": it["number"],
                "url": it["html_url"],
                "title": it["title"],
                "state": it["state"],
            })
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jules/prs", response_model=list[PRInfo])
async def list_jules_prs():
    try:
        gh = GitHubClient()
        items = await gh.list_prs()
        out = []
        for pr in items:
            head_ref = pr.get("head", {}).get("ref")
            out.append({
                "number": pr["number"],
                "url": pr["html_url"],
                "title": pr["title"],
                "state": pr["state"],
                "head_ref": head_ref
            })
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
