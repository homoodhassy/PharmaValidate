"""
PharmaValidate v0.5 - Projects Directory Page
Displays registered validation projects with administrative controls for lifecycle management.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
    QFrame,
)

# Import our database functions
from database.database import get_projects, delete_project


class ProjectsPage(QWidget):

    def __init__(self):
        super().__init__()
        self.workspace_callback = None
        self.build_ui()

    def build_ui(self):
        # Base styling for the directory
        self.setStyleSheet("background-color: #F8FAFC;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Header Section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title = QLabel("📂 Validation Projects Directory")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #0F172A;")
        
        subtitle = QLabel("Browse active protocols, view current assignments, or manage system records.")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # Project Ledger Table
        # -------------------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Project Protocol Name",
            "Target Product",
            "Method Technique",
            "Validation Study",
            "Protocol ID Ref",
            "Assigned Analyst"
        ])

        # --- UI/UX UPGRADES ---
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # Select whole rows instead of single cells
        self.table.setSelectionMode(QAbstractItemView.SingleSelection) # Restrict to single-row selection
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make table strictly read-only
        self.table.setAlternatingRowColors(True)                      # Enable alternating row tints
        self.table.verticalHeader().setVisible(False)                 # Hide row index numbers (looks cleaner)

        # Elegant Slate/Blue Style Rules
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                gridline-color: #E2E8F0;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #334155;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE; /* Light blue highlight */
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: bold;
                border: 1px solid #E2E8F0;
                padding: 8px;
            }
        """)

        # Column Sizing Management
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Force ID column to shrink to its content

        # Wire Double Click launch mechanism
        self.table.cellDoubleClicked.connect(self.open_project_double_click)
        main_layout.addWidget(self.table)

        # -------------------------------------------------------------
        # Administrative Action Control Bar
        # -------------------------------------------------------------
        control_bar = QHBoxLayout()
        control_bar.setSpacing(12)

        # Action 1: Open Selected Project Workspace
        self.btn_open = QPushButton("🚀 Open Selected Workspace")
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #172554;
            }
        """)
        self.btn_open.clicked.connect(self.open_selected_project)
        control_bar.addWidget(self.btn_open)

        # Action 2: Refresh Listings
        self.btn_refresh = QPushButton("🔄 Refresh Ledger")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 6px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_projects)
        control_bar.addWidget(self.btn_refresh)

        control_bar.addStretch()

        # Action 3: Delete Selected Project (Destructive action styled red)
        self.btn_delete = QPushButton("🗑️ Delete Selected Project")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #991B1B;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: 1px solid #FCA5A5;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border: 1px solid #EF4444;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_selected_project)
        control_bar.addWidget(self.btn_delete)

        main_layout.addLayout(control_bar)
        self.load_projects()

    # -----------------------------------------------------------------
    # Data Engine & Operations
    # -----------------------------------------------------------------
    def load_projects(self):
        """Fetches latest project data state from database and populates matrix."""
        rows = get_projects()
        self.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            for column_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # Align values in the center (especially ID, Method, Protocol)
                if column_index in [0, 3, 4, 5]:
                    item.setTextAlignment(Qt.AlignCenter)
                    
                self.table.setItem(row_index, column_index, item)

    def open_project_double_click(self, row, column):
        """Bypasses active grid index and targets the Row ID directly."""
        self.launch_workspace_by_row(row)

    def open_selected_project(self):
        """Triggers workspace routing based on currently highlighted table row."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select a project from the directory list before opening the workspace."
            )
            return
        self.launch_workspace_by_row(selected_row)

    def launch_workspace_by_row(self, row_idx):
        """Resolves target database ID and calls routing shell callback."""
        if self.workspace_callback is None:
            return

        try:
            # Column 0 is guaranteed to hold the unique SQL PRIMARY KEY ID
            project_id = int(self.table.item(row_idx, 0).text())
            self.workspace_callback(project_id)
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Could not launch workspace routing: {str(e)}")

    def delete_selected_project(self):
        """Prompts confirmation window and deletes selected protocol record."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select the target project row you wish to delete."
            )
            return

        try:
            # Extract basic tracking metadata from grid cells
            project_id = int(self.table.item(selected_row, 0).text())
            project_name = self.table.item(selected_row, 1).text()
            protocol_id = self.table.item(selected_row, 5).text()

            # Warning dialogue block
            confirm_msg = (
                f"⚠️ WARNING: You are about to permanently delete the validation project:\n\n"
                f"• Project: {project_name}\n"
                f"• Protocol ID: {protocol_id}\n\n"
                f"This action will erase ALL associated calibration runs, purity checks, "
                f"and validation profiles. THIS CANNOT BE UNDONE.\n\n"
                f"Do you wish to proceed?"
            )

            reply = QMessageBox.question(
                self,
                "Confirm Project Destruction",
                confirm_msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove from database
                delete_project(project_id)
                
                # Refresh table ledger view
                self.load_projects()
                
                QMessageBox.information(
                    self,
                    "Ledger Updated",
                    f"Project '{project_name}' has been deleted successfully."
                )

        except Exception as e:
            QMessageBox.critical(
                self, 
                "Database Integrity Error", 
                f"Failed to execute project deletion: {str(e)}"
            )