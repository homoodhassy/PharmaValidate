"""
PharmaValidate v0.5 - Reports & Protocols Hub
A clean nested tab container hosting active analytical reports and protocol generation views.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

# Import your original reports page and the new protocol compiler page
from ui.reports import ReportsPage
from ui.protocol_page import ProtocolPage


class ReportsHubPage(QWidget):

    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        # Set overall background to match main window theme
        self.setStyleSheet("background-color: #F8FAFC;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # -------------------------------------------------------------
        # 1. Primary Tab Controller (Sleek Professional Tab styling)
        # -------------------------------------------------------------
        self.tab_manager = QTabWidget()
        self.tab_manager.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #64748B;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 24px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid transparent;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1E3A8A; /* Active Blue */
                border: 1px solid #E2E8F0;
                border-bottom-color: #FFFFFF; /* Seamless blending with pane */
            }
            QTabBar::tab:hover:!selected {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)

        # -------------------------------------------------------------
        # 2. Page Instantiation & Assembly
        # -------------------------------------------------------------
        self.reports_tab = ReportsPage()
        self.protocols_tab = ProtocolPage()

        # Add subpages as nested tabs
        self.tab_manager.addTab(self.reports_tab, "📊 Analytics Reports")
        self.tab_manager.addTab(self.protocols_tab, "📑 Protocol Compiler")

        layout.addWidget(self.tab_manager)