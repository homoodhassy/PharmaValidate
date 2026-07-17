"""
PharmaValidate v0.5 - Main Application Window
Coordinates left-bar navigation and layout routing.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
)

from ui.dashboard import DashboardPage
from ui.new_validation import NewValidationPage
from ui.projects import ProjectsPage
from ui.settings import SettingsPage
from ui.project_workspace import ProjectWorkspace

# CHANGED: Import the combined Reports Hub instead of the raw ReportsPage
from ui.reports_hub import ReportsHubPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PharmaValidate v0.5")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # --------------------------
        # Left Menu
        # --------------------------
        menu = QVBoxLayout()

        self.btnDashboard = QPushButton("🏠 Dashboard")
        self.btnValidation = QPushButton("🧪 New Validation")
        self.btnProjects = QPushButton("📂 Projects")
        self.btnReports = QPushButton("📄 Reports & Protocols")  # Updated Text label
        self.btnSettings = QPushButton("⚙ Settings")

        menu.addWidget(self.btnDashboard)
        menu.addWidget(self.btnValidation)
        menu.addWidget(self.btnProjects)
        menu.addWidget(self.btnReports)
        menu.addWidget(self.btnSettings)

        menu.addStretch()

        # --------------------------
        # Pages
        # --------------------------
        self.pages = QStackedWidget()

        self.project_workspace = None
        self.dashboard = DashboardPage()

        self.projects = ProjectsPage()
        self.projects.workspace_callback = self.open_project_workspace

        self.validation = NewValidationPage(self.projects)

        # CHANGED: Instantiate the Tabbed Hub Page here
        self.reports = ReportsHubPage()

        self.settings = SettingsPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.validation)
        self.pages.addWidget(self.projects)
        self.pages.addWidget(self.reports)  # Pointed safely to our tab container
        self.pages.addWidget(self.settings)

        # --------------------------
        # Layout
        # --------------------------
        main_layout.addLayout(menu, 1)
        main_layout.addWidget(self.pages, 5)

        # --------------------------
        # Navigation Connections
        # --------------------------
        self.btnDashboard.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.dashboard)
        )

        self.btnValidation.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.validation)
        )

        self.btnProjects.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.projects)
        )

        self.btnReports.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.reports)
        )

        self.btnSettings.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.settings)
        )

    # -------------------------------------------------
    # Open Project Workspace
    # -------------------------------------------------
    def open_project_workspace(self, project_id):
        workspace = ProjectWorkspace(project_id)
        self.pages.addWidget(workspace)
        self.pages.setCurrentWidget(workspace)