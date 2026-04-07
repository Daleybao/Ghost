import json
from typing import Any
import numpy as np

from .ai_client import AIClient
from .config import settings
from .schemas import AnalyzeResponse, Issue
from .storage import Storage


class Analyzer:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.client = AIClient()

    def embed_issue(self, issue: Issue) -> list[float]:
        text = self._issue_text(issue)
        return self.client.embedding(text)

    def rank_similar(self, issue: Issue, candidates: list[Issue]) -> list[Issue]:
        if not candidates:
            return []

        query_vector = np.array(self.embed_issue(issue), dtype=np.float32)
        query_norm = np.linalg.norm(query_vector) + 1e-8

        scored: list[tuple[Issue, float]] = []
        for candidate in candidates:
            vec = np.array(self.embed_issue(candidate), dtype=np.float32)
            score = float(np.dot(query_vector, vec) / (query_norm * (np.linalg.norm(vec) + 1e-8)))
            scored.append((candidate, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in scored[: settings.top_k]]

    def analyze_issue(self, issue: Issue, similar_issues: list[Issue]) -> AnalyzeResponse:
        prompt = self._build_prompt(issue, similar_issues)
        parsed = self._safe_json(self.client.analyze(prompt))
        report = {
            "issue_key": issue.issue_key,
            "summary": parsed.get("summary", issue.summary),
            "root_cause_candidates": parsed.get("root_cause_candidates", []),
            "evidence": parsed.get("evidence", []),
            "next_steps": parsed.get("next_steps", []),
            "similar_issues": [i.issue_key for i in similar_issues],
            "confidence": float(parsed.get("confidence", 0.5)),
        }
        self.storage.save_report(issue.issue_key, report)
        return AnalyzeResponse(**report)

    def _issue_text(self, issue: Issue) -> str:
        return "\n".join([
            issue.summary,
            issue.description,
            "\n".join(issue.comments[:5]),
            "\n".join(issue.logs[:3]),
        ])

    def _build_prompt(self, issue: Issue, similar_issues: list[Issue]) -> str:
        hist = []
        for i in similar_issues:
            hist.append(
                {
                    "issue_key": i.issue_key,
                    "summary": i.summary,
                    "description": i.description[:1200],
                    "logs": i.logs[:2],
                }
            )

        return f"""
请基于以下新Issue与历史Issue，输出故障分析。
必须输出JSON，字段包括：
- summary: string
- root_cause_candidates: string[]
- evidence: string[]
- next_steps: string[]
- confidence: 0~1 number

新Issue:
{json.dumps(issue.model_dump(), ensure_ascii=False)}

历史Issue:
{json.dumps(hist, ensure_ascii=False)}

要求：
1) 优先基于证据，不要编造。
2) 如果证据不足，要在next_steps里明确补充采集建议。
3) 输出中文。
""".strip()

    def _safe_json(self, content: Any) -> dict[str, Any]:
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        return {
            "summary": "模型输出解析失败，建议重试。",
            "root_cause_candidates": [],
            "evidence": [str(content)[:300]],
            "next_steps": ["重新触发分析，并检查输入日志是否完整。"],
            "confidence": 0.2,
        }
