import json
import numpy as np
from .ai_client import AIClient
from .config import settings
from .models import Issue
from .storage import Storage


class Analyzer:
    def __init__(self, storage: Storage) -> None:
        self.ai = AIClient()
        self.storage = storage

    def _embed(self, issue: Issue) -> np.ndarray:
        txt = "\n".join([issue.summary, issue.description, "\n".join(issue.comments[:5]), "\n".join(issue.logs[:3])])
        return np.array(self.ai.embedding(txt), dtype=np.float32)

    def rank(self, issue: Issue, candidates: list[Issue]) -> list[Issue]:
        if not candidates:
            return []
        q = self._embed(issue)
        qn = np.linalg.norm(q) + 1e-8
        scored = []
        for c in candidates:
            v = self._embed(c)
            sim = float(np.dot(q, v) / (qn * (np.linalg.norm(v) + 1e-8)))
            scored.append((c, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in scored[: settings.top_k]]

    def analyze(self, issue: Issue, similars: list[Issue]) -> dict:
        hist = [{"issue_key": i.issue_key, "summary": i.summary, "description": i.description[:1200], "logs": i.logs[:2]} for i in similars]
        prompt = f"""
请基于以下新Issue与历史Issue，输出故障分析。
必须输出JSON字段: summary, root_cause_candidates, evidence, next_steps, confidence。
新Issue: {json.dumps(issue.__dict__, ensure_ascii=False)}
历史Issue: {json.dumps(hist, ensure_ascii=False)}
""".strip()
        parsed = self.ai.analyze(prompt)
        report = {
            "issue_key": issue.issue_key,
            "summary": parsed.get("summary", issue.summary),
            "root_cause_candidates": parsed.get("root_cause_candidates", []),
            "evidence": parsed.get("evidence", []),
            "next_steps": parsed.get("next_steps", []),
            "similar_issues": [i.issue_key for i in similars],
            "confidence": float(parsed.get("confidence", 0.5)),
        }
        self.storage.save_report(issue.issue_key, report)
        return report
