import json
import sqlite3
from pathlib import Path
from typing import Any

from .config import settings


class Storage:
    def __init__(self) -> None:
        db_path = Path(settings.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                issue_key TEXT PRIMARY KEY,
                report TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def save_report(self, issue_key: str, report: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO reports(issue_key, report)
            VALUES(?, ?)
            ON CONFLICT(issue_key) DO UPDATE SET report=excluded.report
            """,
            (issue_key, json.dumps(report, ensure_ascii=False)),
        )
        self.conn.commit()

    def get_report(self, issue_key: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT report FROM reports WHERE issue_key = ?", (issue_key,)).fetchone()
        if not row:
            return None
        return json.loads(row["report"])
