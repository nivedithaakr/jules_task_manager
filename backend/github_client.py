import os
import httpx
from typing import List, Dict

GITHUB_API = "https://api.github.com"

class GitHubClient:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPO")
        if not token or not repo:
            raise RuntimeError("GITHUB_TOKEN and GITHUB_REPO must be set in .env")
        self.repo = repo
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    async def create_issue_with_label(self, title: str, body: str, labels: list[str]) -> Dict:
        url = f"{GITHUB_API}/repos/{self.repo}/issues"
        payload = {"title": title, "body": body, "labels": labels}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()

    async def list_issues_by_label(self, label: str) -> List[Dict]:
        url = f"{GITHUB_API}/repos/{self.repo}/issues"
        params = {"labels": label, "state": "all", "per_page": 50}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    async def list_prs(self) -> List[Dict]:
        url = f"{GITHUB_API}/repos/{self.repo}/pulls"
        params = {"state": "all", "per_page": 50}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()
