from typing import List
import requests
from .config import settings
from .schemas import Issue


class JiraClient:
    def __init__(self) -> None:
        self.base_urls = [
            settings.jira_base_url.rstrip("/"),
            settings.new_jira_base_url.rstrip("/"),
        ]
        self.headers = {"Accept": "application/json"}
        if settings.jira_api_token:
            self.headers["Authorization"] = f"Bearer {settings.jira_api_token}"

    def _jql_search(self, base_url: str, jql: str, max_results: int) -> list[dict]:
        url = f"{base_url}/rest/api/3/search"
        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ["summary", "description", "comment", "project"],
        }
        resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("issues", [])

    def fetch_issue(self, issue_key: str) -> Issue:
        jql = f"key = {issue_key}"
        last_error: Exception | None = None
        for base_url in self.base_urls:
            try:
                raw = self._jql_search(base_url, jql, max_results=1)
                if raw:
                    return self._to_issue(raw[0])
            except Exception as e:
                last_error = e
        if last_error:
            raise ValueError(f"Issue not found or Jira unreachable for {issue_key}: {last_error}")
        raise ValueError(f"Issue not found: {issue_key}")

    def fetch_recent_issues(self, issue_key: str, limit: int) -> List[Issue]:
        jql = f"key != {issue_key} ORDER BY created DESC"
        all_issues: dict[str, Issue] = {}
        per_jira_limit = max(1, limit)

        for base_url in self.base_urls:
            try:
                raw = self._jql_search(base_url, jql, max_results=per_jira_limit)
                for row in raw:
                    issue = self._to_issue(row)
                    all_issues[issue.issue_key] = issue
            except Exception:
                continue

        return list(all_issues.values())[:limit]

    def _to_issue(self, raw_issue: dict) -> Issue:
        fields = raw_issue.get("fields", {})
        comments = [c.get("body", "") for c in fields.get("comment", {}).get("comments", [])]
        description = self._extract_adf_text(fields.get("description"))
        comments_text = [self._extract_adf_text(c) for c in comments]

        logs = []
        for text in [description, *comments_text]:
            if "Exception" in text or "ERROR" in text or "Traceback" in text:
                logs.append(text)

        return Issue(
            issue_key=raw_issue["key"],
            summary=fields.get("summary", ""),
            description=description,
            comments=comments_text,
            logs=logs,
        )

    def _extract_adf_text(self, adf: dict | str | None) -> str:
        if adf is None:
            return ""
        if isinstance(adf, str):
            return adf
        if not isinstance(adf, dict):
            return str(adf)

        result: list[str] = []

        def walk(node: dict):
            if not isinstance(node, dict):
                return
            if node.get("type") == "text" and "text" in node:
                result.append(node["text"])
            for child in node.get("content", []):
                walk(child)

        walk(adf)
        return "\n".join(result)
