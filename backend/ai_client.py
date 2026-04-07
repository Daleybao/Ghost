import json
import requests
from .config import settings


class AIClient:
    def __init__(self) -> None:
        self.embedding_url = settings.ai_embedding_url
        self.analysis_url = settings.ai_analysis_url
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def embedding(self, text: str) -> list[float]:
        payload = {"text": text}
        if self.model:
            payload["model"] = self.model

        resp = requests.post(self.embedding_url, headers=self._headers(), json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data.get("embedding"), list):
            return data["embedding"]
        if isinstance(data.get("data"), list) and data["data"] and isinstance(data["data"][0], dict):
            emb = data["data"][0].get("embedding")
            if isinstance(emb, list):
                return emb

        raise ValueError(f"Unsupported embedding response: {json.dumps(data)[:300]}")

    def analyze(self, prompt: str) -> dict:
        payload = {"input": prompt, "response_format": "json"}
        if self.model:
            payload["model"] = self.model

        resp = requests.post(self.analysis_url, headers=self._headers(), json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict) and all(k in data for k in ["summary", "root_cause_candidates", "evidence", "next_steps", "confidence"]):
            return data

        text = data.get("output") or data.get("content") or data.get("text")
        if isinstance(text, str):
            return json.loads(text)

        raise ValueError(f"Unsupported analysis response: {json.dumps(data)[:300]}")
