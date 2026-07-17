"""
PharmaValidate v0.5 - Robustness & D.O.E. Validation Module
Includes Traditional OFAT Robustness and a complete 2^3 Factorial DoE
calculation engine to calculate experimental factor main effects.
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import Qt

class RobustnessWindow(QWidget):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.conditions_data = []  # Stores OFAT inputs
        self.doe_rows = []         # Stores DoE run inputs
        
        self.build_ui()
        self.load_project_data()
        self.add_default_conditions()
        self.add_default_doe_design()

    def load_project_data(self):
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))

    def build_ui(self):
        self.setWindowTitle("Robustness & Design of Experiments (D.O.E.)")
        self.resize(1180, 820)
        self.setMinimumWidth(1000)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(container)

        # Header Title
        title = QLabel("Robustness & Experimental Design Workspace")
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#0F172A;")
        scroll_layout.addWidget(title)

        # Project Metadata Card
        projectFrame = QFrame()
        projectFrame.setFrameShape(QFrame.StyledPanel)
        projectFrame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        projectLayout = QGridLayout(projectFrame)
        projectLayout.setContentsMargins(15, 15, 15, 15)
        projectLayout.setSpacing(15)

        self.lblProject = QLabel("-")
        self.lblProduct = QLabel("-")
        self.lblMethod = QLabel("-")

        projectLayout.addWidget(QLabel("<b>Project Name:</b>"), 0, 0)
        projectLayout.addWidget(self.lblProject, 0, 1)
        projectLayout.addWidget(QLabel("<b>Product Target:</b>"), 0, 2)
        projectLayout.addWidget(self.lblProduct, 0, 3)
        projectLayout.addWidget(QLabel("<b>Analytical Method:</b>"), 0, 4)
        projectLayout.addWidget(self.lblMethod, 0, 5)
        scroll_layout.addWidget(projectFrame)

        # ------------------------------------------------------------------
        # Tab Widget Integration (OFAT vs DoE)
        # ------------------------------------------------------------------
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; border-radius: 8px; background: white; }
            QTabBar::tab { background: #F1F5F9; color: #475569; padding: 10px 20px; font-weight: bold; border: 1px solid #E2E8F0; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: white; color: #1E3A8A; border-bottom: 2px solid #1E3A8A; }
        """)
        
        self.tab_ofat = QWidget()
        self.tab_doe = QWidget()
        
        self.tab_widget.addTab(self.tab_ofat, "Traditional OFAT Robustness")
        self.tab_widget.addTab(self.tab_doe, "2³ Full Factorial D.O.E. Engine")
        
        scroll_layout.addWidget(self.tab_widget)

        # Build individual tab workspaces
        self.build_ofat_tab()
        self.build_doe_tab()

        # Save Button Footer
        actions = QHBoxLayout()
        actions.addStretch()
        btnSave = QPushButton("Lock Robustness Matrix")
        btnSave.setStyleSheet("""
            QPushButton { background-color: #10B981; color: white; font-weight: bold; padding: 10px 20px; border-radius: 6px; border:none;}
            QPushButton:hover { background-color: #059669; }
        """)
        btnSave.clicked.connect(self.save_data)
        actions.addWidget(btnSave)
        scroll_layout.addLayout(actions)

    # ------------------------------------------------------------------
    # TAB 1: Traditional OFAT (One-Factor-At-A-Time) UI Construction
    # ------------------------------------------------------------------
    def build_ofat_tab(self):
        layout = QVBoxLayout(self.tab_ofat)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        grid_header = QLabel("Deliberate Parameter Variations & Suitability Output")
        grid_header.setStyleSheet("font-weight: bold; font-size: 15px; color: #0F172A; border-bottom: 2px solid #10B981; padding-bottom: 5px;")
        layout.addWidget(grid_header)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setContentsMargins(0, 10, 0, 10)

        headers = [
            "Deliberate Factor Parameter", 
            "Retention Time (Rt)", 
            "Tailing Factor (T)", 
            "Theoretical Plates (N)", 
            "Assay Result (%)", 
            "Dev. from Nominal (%)", 
            "Suitability Status"
        ]

        for col, text in enumerate(headers):
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            lbl.setStyleSheet("background-color: #F1F5F9; padding: 6px; border-radius: 4px; font-size: 11px;")
            self.grid_layout.addWidget(lbl, 0, col)

        layout.addWidget(self.grid_widget)

        btn_add = QPushButton("+ Add Custom Parametric Variation")
        btn_add.setStyleSheet("""
            QPushButton { background-color: #F1F5F9; color: #475569; border: 1px dashed #CBD5E1; padding: 8px; border-radius: 6px; font-weight: bold;}
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_add.clicked.connect(self.add_custom_condition)
        layout.addWidget(btn_add)

        # Summary Block
        summary_header = QLabel("Robustness Verdict Summary")
        summary_header.setStyleSheet("font-size:15px; font-weight:bold; color:#2C3E50; margin-top:10px;")
        layout.addWidget(summary_header)

        summaryFrame = QFrame()
        summaryFrame.setFrameShape(QFrame.StyledPanel)
        summaryFrame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        summaryLayout = QGridLayout(summaryFrame)
        summaryLayout.setContentsMargins(15, 15, 15, 15)
        summaryLayout.setSpacing(15)

        self.lblMaxDev = QLabel("0.00%")
        self.lblSuitabilityVerdict = QLabel("Pending Data")
        self.lblSuitabilityVerdict.setStyleSheet("font-weight: bold; color: gray; font-size: 13px;")

        summaryLayout.addWidget(QLabel("<b>Max Assay Shift Observed:</b>"), 0, 0)
        summaryLayout.addWidget(self.lblMaxDev, 0, 1)
        summaryLayout.addWidget(QLabel("<b>System Suitability Evaluation:</b>"), 0, 2)
        summaryLayout.addWidget(self.lblSuitabilityVerdict, 0, 3)

        layout.addWidget(summaryFrame)

    # ------------------------------------------------------------------
    # TAB 2: Design of Experiments (D.O.E.) UI Construction
    # ------------------------------------------------------------------
    def build_doe_tab(self):
        layout = QVBoxLayout(self.tab_doe)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("2³ Full Factorial Design - Experimental Factor Screening")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1E3A8A; border-bottom: 2px solid #3B82F6; padding-bottom: 5px;")
        layout.addWidget(title)

        # Factor Configuration Frame
        fact_frame = QFrame()
        fact_frame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        fact_grid = QGridLayout(fact_frame)
        fact_grid.setContentsMargins(12, 12, 12, 12)
        fact_grid.setSpacing(10)

        fact_grid.addWidget(QLabel("<b>Factor Identification</b>"), 0, 0)
        fact_grid.addWidget(QLabel("<b>Low Level (-) Value</b>"), 0, 1)
        fact_grid.addWidget(QLabel("<b>High Level (+) Value</b>"), 0, 2)

        # Factor A
        self.txt_fact_a = QLineEdit("Flow Rate (mL/min)")
        self.txt_fact_a.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_fact_a.textChanged.connect(self.update_doe_labels)
        self.txt_a_low = QLineEdit("0.8")
        self.txt_a_low.setAlignment(Qt.AlignCenter)
        self.txt_a_low.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_a_low.textChanged.connect(self.update_doe_labels)
        self.txt_a_high = QLineEdit("1.2")
        self.txt_a_high.setAlignment(Qt.AlignCenter)
        self.txt_a_high.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_a_high.textChanged.connect(self.update_doe_labels)

        fact_grid.addWidget(self.txt_fact_a, 1, 0)
        fact_grid.addWidget(self.txt_a_low, 1, 1)
        fact_grid.addWidget(self.txt_a_high, 1, 2)

        # Factor B
        self.txt_fact_b = QLineEdit("Column Temp (°C)")
        self.txt_fact_b.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_fact_b.textChanged.connect(self.update_doe_labels)
        self.txt_b_low = QLineEdit("35")
        self.txt_b_low.setAlignment(Qt.AlignCenter)
        self.txt_b_low.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_b_low.textChanged.connect(self.update_doe_labels)
        self.txt_b_high = QLineEdit("45")
        self.txt_b_high.setAlignment(Qt.AlignCenter)
        self.txt_b_high.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_b_high.textChanged.connect(self.update_doe_labels)

        fact_grid.addWidget(self.txt_fact_b, 2, 0)
        fact_grid.addWidget(self.txt_b_low, 2, 1)
        fact_grid.addWidget(self.txt_b_high, 2, 2)

        # Factor C
        self.txt_fact_c = QLineEdit("Buffer pH")
        self.txt_fact_c.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_fact_c.textChanged.connect(self.update_doe_labels)
        self.txt_c_low = QLineEdit("2.8")
        self.txt_c_low.setAlignment(Qt.AlignCenter)
        self.txt_c_low.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_c_low.textChanged.connect(self.update_doe_labels)
        self.txt_c_high = QLineEdit("3.2")
        self.txt_c_high.setAlignment(Qt.AlignCenter)
        self.txt_c_high.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.txt_c_high.textChanged.connect(self.update_doe_labels)

        fact_grid.addWidget(self.txt_fact_c, 3, 0)
        fact_grid.addWidget(self.txt_c_low, 3, 1)
        fact_grid.addWidget(self.txt_c_high, 3, 2)

        layout.addWidget(fact_frame)

        # Orthogonal Run Table Grid
        self.doe_grid_widget = QWidget()
        self.doe_grid_layout = QGridLayout(self.doe_grid_widget)
        self.doe_grid_layout.setSpacing(6)
        self.doe_grid_layout.setContentsMargins(0, 10, 0, 10)

        doe_headers = [
            "Run #", 
            "Factor A Level", 
            "Factor B Level", 
            "Factor C Level", 
            "Target Response Y (e.g. Assay %)"
        ]

        for col, text in enumerate(doe_headers):
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            lbl.setStyleSheet("background-color: #EFF6FF; padding: 6px; border-radius: 4px; font-size: 11px; color:#1E40AF;")
            self.doe_grid_layout.addWidget(lbl, 0, col)

        layout.addWidget(self.doe_grid_widget)

        # D.O.E. Calculation Summary
        summary_doe_header = QLabel("D.O.E. Calculated Main Factor Effects")
        summary_doe_header.setStyleSheet("font-size:15px; font-weight:bold; color:#1E3A8A; margin-top:10px;")
        layout.addWidget(summary_doe_header)

        doe_summary_frame = QFrame()
        doe_summary_frame.setStyleSheet("background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px;")
        doe_summary_layout = QGridLayout(doe_summary_frame)
        doe_summary_layout.setContentsMargins(15, 15, 15, 15)
        doe_summary_layout.setSpacing(15)

        self.lbl_lbl_eff_a = QLabel("<b>Factor A Effect:</b>")
        self.lbl_eff_a = QLabel("0.0000")
        self.lbl_eff_a.setStyleSheet("font-weight: bold; font-size: 13px; color: #0F172A;")

        self.lbl_lbl_eff_b = QLabel("<b>Factor B Effect:</b>")
        self.lbl_eff_b = QLabel("0.0000")
        self.lbl_eff_b.setStyleSheet("font-weight: bold; font-size: 13px; color: #0F172A;")

        self.lbl_lbl_eff_c = QLabel("<b>Factor C Effect:</b>")
        self.lbl_eff_c = QLabel("0.0000")
        self.lbl_eff_c.setStyleSheet("font-weight: bold; font-size: 13px; color: #0F172A;")

        self.lbl_doe_summary = QLabel("Enter experimental data above to see the effects breakdown.")
        self.lbl_doe_summary.setWordWrap(True)
        self.lbl_doe_summary.setStyleSheet("color: #475569; font-size: 12px; font-style: italic;")

        doe_summary_layout.addWidget(self.lbl_lbl_eff_a, 0, 0)
        doe_summary_layout.addWidget(self.lbl_eff_a, 0, 1)
        doe_summary_layout.addWidget(self.lbl_lbl_eff_b, 0, 2)
        doe_summary_layout.addWidget(self.lbl_eff_b, 0, 3)
        doe_summary_layout.addWidget(self.lbl_lbl_eff_c, 0, 4)
        doe_summary_layout.addWidget(self.lbl_eff_c, 0, 5)
        doe_summary_layout.addWidget(self.lbl_doe_summary, 1, 0, 1, 6)

        layout.addWidget(doe_summary_frame)

    # ------------------------------------------------------------------
    # TAB 1: Calculations & Condition Additions (OFAT)
    # ------------------------------------------------------------------
    def add_default_conditions(self):
        defaults = [
            ("Nominal (Standard Method Run)", "4.50", "1.15", "5400", "100.00"),
            ("Flow Rate Low (-0.2 mL/min)", "5.10", "1.18", "5100", "99.40"),
            ("Flow Rate High (+0.2 mL/min)", "3.95", "1.12", "5600", "100.25"),
            ("Column Temp Low (-5 °C)", "4.75", "1.16", "5300", "99.80"),
            ("Column Temp High (+5 °C)", "4.30", "1.13", "5500", "100.10"),
        ]
        for idx, item in enumerate(defaults):
            self.create_condition_row(item[0], item[1], item[2], item[3], item[4], is_nominal=(idx == 0))

    def add_custom_condition(self):
        self.create_condition_row("Mobile Phase Organic Ratio (+2%)", "", "", "", "")

    def create_condition_row(self, name, rt, tailing, plates, assay, is_nominal=False):
        row_idx = len(self.conditions_data) + 1

        txt_name = QLineEdit(name)
        txt_name.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        if is_nominal:
            txt_name.setStyleSheet("padding: 4px; border: 1px solid #10B981; background-color: #F0FDF4; font-weight: bold;")

        txt_rt = QLineEdit(rt)
        txt_rt.setPlaceholderText("0.00")
        txt_rt.setAlignment(Qt.AlignCenter)
        txt_rt.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_rt.textChanged.connect(self.update_calculations)

        txt_tailing = QLineEdit(tailing)
        txt_tailing.setPlaceholderText("0.00")
        txt_tailing.setAlignment(Qt.AlignCenter)
        txt_tailing.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_tailing.textChanged.connect(self.update_calculations)

        txt_plates = QLineEdit(plates)
        txt_plates.setPlaceholderText("0000")
        txt_plates.setAlignment(Qt.AlignCenter)
        txt_plates.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_plates.textChanged.connect(self.update_calculations)

        txt_assay = QLineEdit(assay)
        txt_assay.setPlaceholderText("0.00")
        txt_assay.setAlignment(Qt.AlignRight)
        txt_assay.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_assay.textChanged.connect(self.update_calculations)

        lbl_dev = QLabel("0.00%")
        lbl_dev.setAlignment(Qt.AlignRight)
        lbl_dev.setStyleSheet("color: #475569; padding-right: 5px;")

        lbl_status = QLabel("PASS")
        lbl_status.setAlignment(Qt.AlignCenter)
        lbl_status.setStyleSheet("font-weight: bold; color: green;")

        self.grid_layout.addWidget(txt_name, row_idx, 0)
        self.grid_layout.addWidget(txt_rt, row_idx, 1)
        self.grid_layout.addWidget(txt_tailing, row_idx, 2)
        self.grid_layout.addWidget(txt_plates, row_idx, 3)
        self.grid_layout.addWidget(txt_assay, row_idx, 4)
        self.grid_layout.addWidget(lbl_dev, row_idx, 5)
        self.grid_layout.addWidget(lbl_status, row_idx, 6)

        self.conditions_data.append({
            "name": txt_name,
            "rt": txt_rt,
            "tailing": txt_tailing,
            "plates": txt_plates,
            "assay": txt_assay,
            "dev": lbl_dev,
            "status": lbl_status,
            "is_nominal": is_nominal
        })
        self.update_calculations()

    def update_calculations(self):
        nominal_assay = None
        for row in self.conditions_data:
            if row["is_nominal"]:
                try:
                    nominal_assay = float(row["assay"].text()) if row["assay"].text() else None
                except ValueError:
                    pass

        max_dev = 0.0
        all_passed = True

        for row in self.conditions_data:
            try:
                tailing = float(row["tailing"].text()) if row["tailing"].text() else 0.0
                plates = float(row["plates"].text()) if row["plates"].text() else 0.0
                assay = float(row["assay"].text()) if row["assay"].text() else 0.0
            except ValueError:
                tailing, plates, assay = 0.0, 0.0, 0.0

            dev_val = 0.0
            if nominal_assay and nominal_assay > 0 and not row["is_nominal"]:
                dev_val = abs(assay - nominal_assay) / nominal_assay * 100
                row["dev"].setText(f"{dev_val:.2f}%")
                max_dev = max(max_dev, dev_val)
            else:
                row["dev"].setText("0.00%")

            row_fails = False
            if tailing > 2.0 or (plates > 0 and plates < 2000) or dev_val > 2.0:
                row_fails = True

            if row_fails:
                row["status"].setText("FAIL")
                row["status"].setStyleSheet("color: red; font-weight: bold;")
                all_passed = False
            else:
                row["status"].setText("PASS")
                row["status"].setStyleSheet("color: green; font-weight: bold;")

        self.lblMaxDev.setText(f"{max_dev:.2f}%")
        if all_passed and len(self.conditions_data) > 0:
            self.lblSuitabilityVerdict.setText("PASS - System suitability criteria sustained throughout all deviations.")
            self.lblSuitabilityVerdict.setStyleSheet("color: green; font-weight: bold; font-size: 13px;")
        else:
            self.lblSuitabilityVerdict.setText("FAIL - Tailing, plate count, or recovery limits breached under variations.")
            self.lblSuitabilityVerdict.setStyleSheet("color: red; font-weight: bold; font-size: 13px;")

    # ------------------------------------------------------------------
    # TAB 2: Design of Experiments (D.O.E.) Calculation Logic
    # ------------------------------------------------------------------
    def add_default_doe_design(self):
        # 8 Standard Orthogonal Runs representing 2^3 full factorial design
        # Columns: sign levels for (A, B, C) and standard target test assay answers
        defaults = [
            ("-", "-", "-", "100.12"),
            ("+", "-", "-", "99.85"),
            ("-", "+", "-", "100.45"),
            ("+", "+", "-", "100.20"),
            ("-", "-", "+", "98.70"),
            ("+", "-", "+", "98.42"),
            ("-", "+", "+", "99.10"),
            ("+", "+", "+", "98.85"),
        ]
        
        for idx, (sa, sb, sc, res) in enumerate(defaults):
            row_idx = idx + 1
            
            lbl_run = QLabel(f"Run {row_idx}")
            lbl_run.setAlignment(Qt.AlignCenter)
            
            lbl_a = QLabel(sa)
            lbl_a.setAlignment(Qt.AlignCenter)
            lbl_a.setStyleSheet("font-weight: bold; color: #1E40AF;")
            
            lbl_b = QLabel(sb)
            lbl_b.setAlignment(Qt.AlignCenter)
            lbl_b.setStyleSheet("font-weight: bold; color: #1E40AF;")
            
            lbl_c = QLabel(sc)
            lbl_c.setAlignment(Qt.AlignCenter)
            lbl_c.setStyleSheet("font-weight: bold; color: #1E40AF;")
            
            txt_y = QLineEdit(res)
            txt_y.setPlaceholderText("0.00")
            txt_y.setAlignment(Qt.AlignRight)
            txt_y.setStyleSheet("padding:4px; border: 1px solid #CBD5E1; border-radius: 4px;")
            txt_y.textChanged.connect(self.calculate_doe_effects)

            self.doe_grid_layout.addWidget(lbl_run, row_idx, 0)
            self.doe_grid_layout.addWidget(lbl_a, row_idx, 1)
            self.doe_grid_layout.addWidget(lbl_b, row_idx, 2)
            self.doe_grid_layout.addWidget(lbl_c, row_idx, 3)
            self.doe_grid_layout.addWidget(txt_y, row_idx, 4)

            self.doe_rows.append({
                "sa": sa, "sb": sb, "sc": sc, "y": txt_y,
                "lbl_a": lbl_a, "lbl_b": lbl_b, "lbl_c": lbl_c
            })
            
        self.update_doe_labels()
        self.calculate_doe_effects()

    def update_doe_labels(self):
        """Refreshes labels to show the current factor names and level parameters."""
        fact_a = self.txt_fact_a.text() if self.txt_fact_a.text() else "Factor A"
        fact_b = self.txt_fact_b.text() if self.txt_fact_b.text() else "Factor B"
        fact_c = self.txt_fact_c.text() if self.txt_fact_c.text() else "Factor C"

        self.lbl_lbl_eff_a.setText(f"<b>{fact_a} Main Effect:</b>")
        self.lbl_lbl_eff_b.setText(f"<b>{fact_b} Main Effect:</b>")
        self.lbl_lbl_eff_c.setText(f"<b>{fact_c} Main Effect:</b>")

        low_a = self.txt_a_low.text()
        high_a = self.txt_a_high.text()
        low_b = self.txt_b_low.text()
        high_b = self.txt_b_high.text()
        low_c = self.txt_c_low.text()
        high_c = self.txt_c_high.text()

        for r in self.doe_rows:
            sa_val = f"High ({high_a})" if r["sa"] == "+" else f"Low ({low_a})"
            sb_val = f"High ({high_b})" if r["sb"] == "+" else f"Low ({low_b})"
            sc_val = f"High ({high_c})" if r["sc"] == "+" else f"Low ({low_c})"
            
            r["lbl_a"].setText(sa_val)
            r["lbl_b"].setText(sb_val)
            r["lbl_c"].setText(sc_val)
            
        self.calculate_doe_effects()

    def calculate_doe_effects(self):
        """Calculates the multivariable Main Effect values for Factors A, B, and C."""
        try:
            # 1. Gather Response Values
            y = []
            for r in self.doe_rows:
                y_str = r["y"].text().strip()
                y_val = float(y_str) if y_str else 0.0
                y.append(y_val)

            if len(y) < 8:
                return

            # 2. Main Effects Formula: Mean(Y at +) - Mean(Y at -)
            # A+ runs: index [1, 3, 5, 7] | A- runs: index [0, 2, 4, 6]
            mean_a_plus = (y[1] + y[3] + y[5] + y[7]) / 4.0
            mean_a_minus = (y[0] + y[2] + y[4] + y[6]) / 4.0
            eff_a = mean_a_plus - mean_a_minus

            # B+ runs: index [2, 3, 6, 7] | B- runs: index [0, 1, 4, 5]
            mean_b_plus = (y[2] + y[3] + y[6] + y[7]) / 4.0
            mean_b_minus = (y[0] + y[1] + y[4] + y[5]) / 4.0
            eff_b = mean_b_plus - mean_b_minus

            # C+ runs: index [4, 5, 6, 7] | C- runs: index [0, 1, 2, 3]
            mean_c_plus = (y[4] + y[5] + y[6] + y[7]) / 4.0
            mean_c_minus = (y[0] + y[1] + y[2] + y[3]) / 4.0
            eff_c = mean_c_plus - mean_c_minus

            # 3. Update Labels
            self.lbl_eff_a.setText(f"{eff_a:+.4f}")
            self.lbl_eff_b.setText(f"{eff_b:+.4f}")
            self.lbl_eff_c.setText(f"{eff_c:+.4f}")

            # 4. Critical Factor Diagnostics Analysis
            fact_a = self.txt_fact_a.text() if self.txt_fact_a.text() else "Factor A"
            fact_b = self.txt_fact_b.text() if self.txt_fact_b.text() else "Factor B"
            fact_c = self.txt_fact_c.text() if self.txt_fact_c.text() else "Factor C"

            effects = [
                (abs(eff_a), fact_a, eff_a),
                (abs(eff_b), fact_b, eff_b),
                (abs(eff_c), fact_c, eff_c)
            ]
            effects.sort(reverse=True, key=lambda x: x[0])
            
            dominant = effects[0]
            if dominant[0] > 0.0001:
                direction = "increases" if dominant[2] > 0 else "decreases"
                self.lbl_doe_summary.setText(
                    f"💡 <b>Critical Diagnostic Found:</b> Factor <b>{dominant[1]}</b> has the strongest influence on this method response. "
                    f"Shifting it from Low to High causes an average shift of <b>{dominant[2]:+.3f}</b> in response. "
                    f"Ensure strict controls are placed on this specific factor during routing analysis!"
                )
                self.lbl_doe_summary.setStyleSheet("color: #1E3A8A; font-size: 12px; font-weight: normal;")
            else:
                self.lbl_doe_summary.setText("No significant factor effect observed within testing levels.")
                self.lbl_doe_summary.setStyleSheet("color: #475569; font-size: 12px; font-style: italic;")

        except ValueError:
            # Handles scenarios when typing is in progress
            pass

    # ------------------------------------------------------------------
    # Universal Save Handler
    # ------------------------------------------------------------------
    def save_data(self):
        QMessageBox.information(self, "Save Robustness & D.O.E.", "Robustness OFAT parameters and D.O.E. screening matrices successfully locked!")