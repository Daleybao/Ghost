import json
import sys
import requests
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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jira AI Analyzer - Qt UI")
        self.resize(900, 700)

        self.backend_url = QLineEdit("http://127.0.0.1:8000")
        self.issue_key = QLineEdit("")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        analyze_btn = QPushButton("实时分析Issue")
        analyze_btn.clicked.connect(self.analyze_issue)

        report_btn = QPushButton("查询已保存报告")
        report_btn.clicked.connect(self.get_report)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("后端地址"))
        layout.addWidget(self.backend_url)
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

        base = self.backend_url.text().rstrip("/")
        try:
            resp = requests.post(f"{base}/analyze/{issue_key}", timeout=300)
            resp.raise_for_status()
            self.output.setPlainText(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def get_report(self) -> None:
        issue_key = self.issue_key.text().strip()
        if not issue_key:
            QMessageBox.warning(self, "提示", "请先输入 Issue Key")
            return

        base = self.backend_url.text().rstrip("/")
        try:
            resp = requests.get(f"{base}/report/{issue_key}", timeout=60)
            resp.raise_for_status()
            self.output.setPlainText(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
