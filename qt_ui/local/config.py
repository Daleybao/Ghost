import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_model: str = os.getenv("AI_MODEL", "")
    ai_embedding_url: str = os.getenv("AI_EMBEDDING_URL", "")
    ai_analysis_url: str = os.getenv("AI_ANALYSIS_URL", "")

    jira_base_url: str = os.getenv("JIRA_BASE_URL", "https://jira.n.xiaomi.com")
    new_jira_base_url: str = os.getenv("NEW_JIRA_BASE_URL", "https://jira-phone.mioffice.cn")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")

    db_path: str = os.getenv("DB_PATH", "./data/app.db")
    top_k: int = int(os.getenv("TOP_K", "5"))
    candidate_pool_size: int = int(os.getenv("CANDIDATE_POOL_SIZE", "100"))


settings = Settings()
