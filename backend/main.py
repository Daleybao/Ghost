from fastapi import FastAPI, HTTPException

from .analyzer import Analyzer
from .config import settings
from .jira_client import JiraClient
from .schemas import WebhookPayload
from .storage import Storage

app = FastAPI(title="Jira AI Analyzer")

storage = Storage()
analyzer = Analyzer(storage)
jira = JiraClient()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze/{issue_key}")
def analyze(issue_key: str) -> dict:
    try:
        issue = jira.fetch_issue(issue_key)
        recent_issues = jira.fetch_recent_issues(
            issue_key=issue_key,
            limit=settings.candidate_pool_size,
        )
        similar_issues = analyzer.rank_similar(issue, recent_issues)
        report = analyzer.analyze_issue(issue, similar_issues)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/webhook/jira")
def jira_webhook(payload: WebhookPayload) -> dict:
    return analyze(payload.issue_key)


@app.get("/report/{issue_key}")
def get_report(issue_key: str) -> dict:
    report = storage.get_report(issue_key)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
