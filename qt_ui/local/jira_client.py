import requests
from .config import settings
from .models import Issue


class JiraClient:
    def __init__(self) -> None:
        self.base_urls = [settings.jira_base_url.rstrip('/'), settings.new_jira_base_url.rstrip('/')]
        self.headers = {"Accept": "application/json"}
        if settings.jira_api_token:
            self.headers["Authorization"] = f"Bearer {settings.jira_api_token}"

    def _search(self, base_url: str, jql: str, max_results: int) -> list[dict]:
        url = f"{base_url}/rest/api/3/search"
        payload = {"jql": jql, "maxResults": max_results, "fields": ["summary", "description", "comment", "project"]}
        resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json().get("issues", [])

    def fetch_issue(self, issue_key: str) -> Issue:
        for base_url in self.base_urls:
            try:
                raw = self._search(base_url, f"key = {issue_key}", 1)
                if raw:
                    return self._to_issue(raw[0])
            except Exception:
                continue
        raise ValueError(f"Issue not found: {issue_key}")

    def fetch_recent(self, issue_key: str, limit: int) -> list[Issue]:
        all_items: dict[str, Issue] = {}
        jql = f"key != {issue_key} ORDER BY created DESC"
        for base_url in self.base_urls:
            try:
                raw = self._search(base_url, jql, limit)
                for r in raw:
                    issue = self._to_issue(r)
                    all_items[issue.issue_key] = issue
            except Exception:
                continue
        return list(all_items.values())[:limit]

    def _to_issue(self, raw_issue: dict) -> Issue:
        fields = raw_issue.get("fields", {})
        comments = [c.get("body", "") for c in fields.get("comment", {}).get("comments", [])]
        description = self._extract_adf(fields.get("description"))
        comments_text = [self._extract_adf(c) for c in comments]
        logs = [t for t in [description, *comments_text] if "Exception" in t or "ERROR" in t or "Traceback" in t]
        return Issue(raw_issue["key"], fields.get("summary", ""), description, comments_text, logs)

    def _extract_adf(self, adf):
        if adf is None:
            return ""
        if isinstance(adf, str):
            return adf
        if not isinstance(adf, dict):
            return str(adf)
        out = []

        def walk(node):
            if not isinstance(node, dict):
                return
            if node.get("type") == "text" and "text" in node:
                out.append(node["text"])
            for child in node.get("content", []):
                walk(child)

        walk(adf)
        return "\n".join(out)
