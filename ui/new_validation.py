"""
PharmaValidate v0.5 - New Validation Page
Polished form interface for creating new analytical validation projects.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QFrame,
    QFormLayout,
)

from database.database import create_project


class NewValidationPage(QWidget):

    def __init__(self, projects_page):
        super().__init__()
        self.projects_page = projects_page
        self.build_ui()

    def build_ui(self):
        # Base Page Styling
        self.setStyleSheet("background-color: #F8FAFC;")
        
        # Root Layout (Centered horizontally)
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(40, 40, 40, 40)
        
        # Form Container Frame (Sleek Form Card)
        form_card = QFrame()
        form_card.setFixedWidth(550)  # Restrict width so it doesn't stretch on wide screens
        form_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                border: none;
            }
            QLineEdit, QComboBox {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #0F172A;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #1E3A8A; /* Theme primary blue */
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #172554;
            }
            QPushButton:pressed {
                background-color: #0F172A;
            }
        """)
        
        card_layout = QVBoxLayout(form_card)
        card_layout.setSpacing(18)
        
        # -------------------------------------------------------------
        # 1. Header Section
        # -------------------------------------------------------------
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title = QLabel("🧪 New Validation Registry")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0F172A;")
        
        subtitle = QLabel("Register a standard analytical validation study inside the secure ledger.")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        card_layout.addLayout(header_layout)

        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #F1F5F9;")
        card_layout.addWidget(line)

        # -------------------------------------------------------------
        # 2. Form Fields (Structured via Form Layout)
        # -------------------------------------------------------------
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # Helper styling for form row labels
        lbl_style = "font-weight: bold; color: #475569; font-size: 13px; margin-top: 5px;"

        # Field A: Project Name
        lbl_proj = QLabel("Project Name:")
        lbl_proj.setStyleSheet(lbl_style)
        self.projectName = QLineEdit()
        self.projectName.setPlaceholderText("e.g., Cetirizine HCl Validation Project")
        form_layout.addRow(lbl_proj, self.projectName)

        # Field B: Product Name (CHANGED TO MANUAL TEXT ENTRY)
        lbl_prod = QLabel("Target Product:")
        lbl_prod.setStyleSheet(lbl_style)
        self.product = QLineEdit()
        self.product.setPlaceholderText("e.g., Cetirizine Hydrochloride Oral Solution (5 mg/5 mL)")
        form_layout.addRow(lbl_prod, self.product)

        # Field C: Method Dropdown
        lbl_meth = QLabel("Method Technique:")
        lbl_meth.setStyleSheet(lbl_style)
        self.method = QComboBox()
        self.method.addItems([
            "HPLC (RP-HPLC)",
            "UV-Vis Spectrophotometry",
            "Gas Chromatography (GC)",
            "Titrimetric Analysis",
        ])
        form_layout.addRow(lbl_meth, self.method)

        # Field D: Validation Type Dropdown
        lbl_val = QLabel("Validation Type:")
        lbl_val.setStyleSheet(lbl_style)
        self.validation = QComboBox()
        self.validation.addItems([
            "Related Substances",
            "Assay",
            "Dissolution",
        ])
        form_layout.addRow(lbl_val, self.validation)

        # Field E: Protocol Number
        lbl_prot = QLabel("Protocol ID:")
        lbl_prot.setStyleSheet(lbl_style)
        self.protocol = QLineEdit()
        self.protocol.setPlaceholderText("e.g., VAL-PRO-2026-001")
        form_layout.addRow(lbl_prot, self.protocol)

        # Field F: Analyst Name
        lbl_analyst = QLabel("QC Analyst:")
        lbl_analyst.setStyleSheet(lbl_style)
        self.analyst = QLineEdit()
        self.analyst.setPlaceholderText("e.g., Osamah (QC Analyst)")
        form_layout.addRow(lbl_analyst, self.analyst)

        card_layout.addLayout(form_layout)

        # -------------------------------------------------------------
        # 3. Action Buttons
        # -------------------------------------------------------------
        self.btnSave = QPushButton("Register New Project 🚀")
        self.btnSave.clicked.connect(self.save_project)
        card_layout.addWidget(self.btnSave)

        # Add card to central base frame with centering alignment
        root_layout.addStretch()
        root_layout.addWidget(form_card)
        root_layout.addStretch()

    def save_project(self):
        # Basic validation checks
        if not self.projectName.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a Project Name to proceed.",
            )
            return

        if not self.product.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter the Target Product details (e.g., Name, Strength, Dosage Form).",
            )
            return

        if not self.protocol.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a valid Protocol ID Reference.",
            )
            return

        if not self.analyst.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please assign an Active QC Analyst to this protocol.",
            )
            return

        # Write safely to DB using text() instead of currentText() for Product
        create_project(
            self.projectName.text().strip(),
            self.product.text().strip(),
            self.method.currentText(),
            self.validation.currentText(),
            self.protocol.text().strip(),
            self.analyst.text().strip(),
        )

        # Refresh project listings dashboard in the background
        self.projects_page.load_projects()

        QMessageBox.information(
            self,
            "Validation Protocol Initiated",
            "Project was successfully registered to database!",
        )

        # Clear active input fields
        self.projectName.clear()
        self.product.clear()
        self.protocol.clear()
        self.analyst.clear()