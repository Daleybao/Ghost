import json
import sys
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from backend.analyzer import Analyzer
from backend.jira_client import JiraClient
from backend.storage import Storage
from backend.config import settings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jira AI Analyzer - 纯Qt本地版")
        self.resize(900, 700)

        self.storage = Storage()
        self.analyzer = Analyzer(self.storage)
        self.jira = JiraClient()

        self.issue_key = QLineEdit("")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        analyze_btn = QPushButton("实时分析Issue")
        analyze_btn.clicked.connect(self.analyze_issue)

        report_btn = QPushButton("查询本地报告")
        report_btn.clicked.connect(self.get_report)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("运行模式：纯Qt本地运行（无后端服务）"))
        layout.addWidget(QLabel("Issue Key (如 OPS-123)"))
        layout.addWidget(self.issue_key)
        layout.addWidget(analyze_btn)
        layout.addWidget(report_btn)
        layout.addWidget(QLabel("输出"))
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def analyze_issue(self) -> None:
        issue_key = self.issue_key.text().strip()
        if not issue_key:
            QMessageBox.warning(self, "提示", "请先输入 Issue Key")
            return

        try:
            issue = self.jira.fetch_issue(issue_key)
            candidates = self.jira.fetch_recent_issues(issue_key=issue_key, limit=settings.candidate_pool_size)
            similar = self.analyzer.rank_similar(issue, candidates)
            report = self.analyzer.analyze_issue(issue, similar)
            self.output.setPlainText(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def get_report(self) -> None:
        issue_key = self.issue_key.text().strip()
        if not issue_key:
            QMessageBox.warning(self, "提示", "请先输入 Issue Key")
            return

        try:
            report = self.storage.get_report(issue_key)
            if not report:
                QMessageBox.information(self, "提示", "本地没有该 Issue 的分析报告")
                return
            self.output.setPlainText(json.dumps(report, ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
