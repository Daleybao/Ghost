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

from qt_ui.local.analyzer import Analyzer
from qt_ui.local.config import settings
from qt_ui.local.jira_client import JiraClient
from qt_ui.local.storage import Storage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jira AI Analyzer - 纯本地 Qt")
        self.resize(900, 700)

        self.jira = JiraClient()
        self.storage = Storage()
        self.analyzer = Analyzer(self.storage)

        self.issue_key = QLineEdit("")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        analyze_btn = QPushButton("实时分析Issue（本地）")
        analyze_btn.clicked.connect(self.analyze_issue)

        report_btn = QPushButton("查询本地报告")
        report_btn.clicked.connect(self.get_report)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("纯本地模式：不需要后端服务"))
        layout.addWidget(QLabel(f"候选问题数量: {settings.candidate_pool_size}, TopK: {settings.top_k}"))
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
            candidates = self.jira.fetch_recent(issue_key, settings.candidate_pool_size)
            similars = self.analyzer.rank(issue, candidates)
            report = self.analyzer.analyze(issue, similars)
            self.output.setPlainText(json.dumps(report, ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def get_report(self) -> None:
        issue_key = self.issue_key.text().strip()
        if not issue_key:
            QMessageBox.warning(self, "提示", "请先输入 Issue Key")
            return

        report = self.storage.get_report(issue_key)
        if not report:
            QMessageBox.information(self, "提示", "本地没有该 issue 的报告")
            return
        self.output.setPlainText(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
