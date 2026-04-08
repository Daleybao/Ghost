import json
import requests
from .config import settings


class AIClient:
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"
        return headers

    def embedding(self, text: str) -> list[float]:
        payload = {"text": text}
        if settings.ai_model:
            payload["model"] = settings.ai_model
        resp = requests.post(settings.ai_embedding_url, headers=self._headers(), json=payload, timeout=60)
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
        if settings.ai_model:
            payload["model"] = settings.ai_model
        resp = requests.post(settings.ai_analysis_url, headers=self._headers(), json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "summary" in data:
            return data
        text = data.get("output") or data.get("content") or data.get("text")
        if isinstance(text, str):
            return json.loads(text)
        raise ValueError(f"Unsupported analysis response: {json.dumps(data)[:300]}")
