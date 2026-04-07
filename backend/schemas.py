from pydantic import BaseModel, Field
from typing import List


class Issue(BaseModel):
    issue_key: str
    summary: str
    description: str = ""
    comments: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    issue_key: str
    summary: str
    root_cause_candidates: List[str]
    evidence: List[str]
    next_steps: List[str]
    similar_issues: List[str]
    confidence: float


class WebhookPayload(BaseModel):
    issue_key: str
