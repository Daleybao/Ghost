from dataclasses import dataclass, field


@dataclass
class Issue:
    issue_key: str
    summary: str
    description: str = ""
    comments: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
