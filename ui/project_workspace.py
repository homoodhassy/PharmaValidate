"""
PharmaValidate v0.5 - Project Workspace UI
Central layout managing state routing and execution of validation modules.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QGridLayout,
    QSizePolicy,
)

from database.database import get_project
from ui.accuracy_window import AccuracyWindow
from ui.precision_window import PrecisionWindow
from ui.linearity_window import LinearityWindow
from ui.specificity_window import SpecificityWindow
from ui.robustness_window import RobustnessWindow
from ui.rel_sub_window import RelSubWindow  # <-- IMPORTED RELATED SUBSTANCES WINDOW


class ModuleCard(QFrame):
    """Reusable visual card displaying status for validation modules."""

    def __init__(self, title: str, description: str, enabled: bool = False):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                background: white;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #0F172A;
            }
            QLabel#desc {
                color: #64748B;
                font-size: 12px;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #172554;
            }
            QPushButton:disabled {
                background-color: #E2E8F0;
                color: #94A3B8;
            }
        """)

        layout = QVBoxLayout(self)

        lblTitle = QLabel(title)
        lblTitle.setObjectName("title")

        lblDesc = QLabel(description)
        lblDesc.setObjectName("desc")
        lblDesc.setWordWrap(True)

        self.button = QPushButton("Open Workspace")
        self.button.setEnabled(enabled)

        layout.addWidget(lblTitle)
        layout.addWidget(lblDesc)
        layout.addStretch()
        layout.addWidget(self.button)


class ProjectWorkspace(QWidget):

    def __init__(self, project_id):
        super().__init__()

        self.project_id = project_id
        self.project = get_project(project_id)

        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)

        # ------------------------------------------------------------------
        # Header Area
        # ------------------------------------------------------------------
        title = QLabel("Project Workspace")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #0F172A;")

        subtitle = QLabel("Central workspace for managing validation activities.")
        subtitle.setStyleSheet("color: #64748B;")

        root.addWidget(title)
        root.addWidget(subtitle)

        # ------------------------------------------------------------------
        # Project Metadata Frame
        # ------------------------------------------------------------------
        info = QFrame()
        info.setFrameShape(QFrame.StyledPanel)
        info.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")

        infoLayout = QGridLayout(info)
        infoLayout.setHorizontalSpacing(30)
        infoLayout.setVerticalSpacing(10)

        if self.project:
            labels = [
                ("Project", self.project[1]),
                ("Product Name", self.project[2]),
                ("Analytical Method", self.project[3]),
                ("Validation Type", self.project[4]),
                ("Protocol ID Reference", self.project[5]),
                ("Assigned QC Analyst", self.project[6]),
            ]

            for row, (name, value) in enumerate(labels):
                lblName = QLabel(f"<b>{name}:</b>")
                lblValue = QLabel(str(value))
                infoLayout.addWidget(lblName, row, 0)
                infoLayout.addWidget(lblValue, row, 1)
        else:
            infoLayout.addWidget(QLabel("Project could not be loaded."), 0, 0)

        root.addWidget(info)

        # ------------------------------------------------------------------
        # Project Status Panel
        # ------------------------------------------------------------------
        statusFrame = QFrame()
        statusFrame.setFrameShape(QFrame.StyledPanel)
        statusFrame.setStyleSheet("background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px;")

        statusLayout = QHBoxLayout(statusFrame)
        statusLayout.setContentsMargins(15, 10, 15, 10)

        statusLabel = QLabel("<b>Validation Suite Status</b>")
        statusLabel.setStyleSheet("color: #166534;")
        statusLayout.addWidget(statusLabel)
        statusLayout.addStretch()
        
        statusText = QLabel("Ready for Active Laboratory Verification Runs")
        statusText.setStyleSheet("color: #166534; font-weight: bold;")
        statusLayout.addWidget(statusText)

        root.addWidget(statusFrame)

        # ------------------------------------------------------------------
        # Dynamic Modules Grid Layout (3 Rows, 2 Columns)
        # ------------------------------------------------------------------
        lblModules = QLabel("Validation Modules")
        lblModules.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A; margin-top: 5px;")
        root.addWidget(lblModules)

        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(15)

        accuracy = ModuleCard(
            "Accuracy (Recovery)",
            "Determine spiked analyte recoveries at 50%, 100%, and 150% target levels.",
            enabled=True,
        )

        precision = ModuleCard(
            "Precision",
            "Assess Method Repeatability & Intermediate Precision across multiple analysts/days.",
            enabled=True,
        )

        linearity = ModuleCard(
            "Linearity & Range",
            "Generate linear regression models, R², correlation coordinates, and % y-intercept.",
            enabled=True,
        )

        specificity = ModuleCard(
            "Specificity & Selectivity",
            "Verify method discrimination against placebo interference, impurities, and diluent blanks.",
            enabled=True,
        )

        robustness = ModuleCard(
            "Robustness Evaluation",
            "Evaluate deliberate parametric drifts in temperature, flow rate, and mobile phases.",
            enabled=True,
        )

        # Replacing the placeholder with our active Related Substances Module!
        related_substances = ModuleCard(
            "Related Substances (Impurities)",
            "Analyze RRF, linearity targets, sensitivity limits (LOD/LOQ), and recovery margins.",
            enabled=True,
        )

        grid.addWidget(accuracy, 0, 0)
        grid.addWidget(precision, 0, 1)
        grid.addWidget(linearity, 1, 0)
        grid.addWidget(specificity, 1, 1)
        grid.addWidget(robustness, 2, 0)
        grid.addWidget(related_substances, 2, 1) # Placed in Row 2, Col 1

        root.addLayout(grid)

        # Connections
        self.btnAccuracy = accuracy.button
        self.btnAccuracy.clicked.connect(self.open_accuracy_window)

        self.btnPrecision = precision.button
        self.btnPrecision.clicked.connect(self.open_precision_window)

        self.btnLinearity = linearity.button
        self.btnLinearity.clicked.connect(self.open_linearity_window)

        self.btnSpecificity = specificity.button
        self.btnSpecificity.clicked.connect(self.open_specificity_window)

        self.btnRobustness = robustness.button
        self.btnRobustness.clicked.connect(self.open_robustness_window)

        self.btnRelatedSubstances = related_substances.button  # <-- WIRED RELATED SUBSTANCES BUTTON
        self.btnRelatedSubstances.clicked.connect(self.open_related_substances_window)

        root.addStretch()

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

    # ------------------------------------------------------------------
    # Action Handlers
    # ------------------------------------------------------------------
    def open_accuracy_window(self):
        try:
            self.acc_window = AccuracyWindow(project=self.project)
            self.acc_window.show()
        except Exception as e:
            print(f"\n--- ERROR ACCURACY WINDOW: {e} ---")

    def open_precision_window(self):
        try:
            self.prec_window = PrecisionWindow(project=self.project)
            self.prec_window.show()
        except Exception as e:
            print(f"\n--- ERROR PRECISION WINDOW: {e} ---")

    def open_linearity_window(self):
        try:
            self.line_window = LinearityWindow(project=self.project)
            self.line_window.show()
        except Exception as e:
            print(f"\n--- ERROR LINEARITY WINDOW: {e} ---")

    def open_specificity_window(self):
        """Launches Specificity verification module."""
        try:
            self.spec_window = SpecificityWindow(project=self.project)
            self.spec_window.show()
        except Exception as e:
            print(f"\n--- ERROR SPECIFICITY WINDOW: {e} ---")

    def open_robustness_window(self):
        """Launches Robustness parameters validation module."""
        try:
            self.rob_window = RobustnessWindow(project=self.project)
            self.rob_window.show()
        except Exception as e:
            print(f"\n--- ERROR ROBUSTNESS WINDOW: {e} ---")

    def open_related_substances_window(self):
        """Launches the full Related Substances Validation Suite window."""
        try:
            self.rel_sub_window = RelSubWindow(project=self.project)
            self.rel_sub_window.show()
        except Exception as e:
            print(f"\n--- ERROR RELATED SUBSTANCES WINDOW: {e} ---")