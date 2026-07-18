import math
import os
import sys
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
)
from PySide6.QtCore import Qt

# Dynamic fallback path handling to safely locate root modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import save_precision, _update_summary_status, update_overall_status
from calculations.precision_calculator import PrecisionCalculator

class PrecisionWindow(QWidget):
    ALPHA = 0.05
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.rep_inputs = []  # Analyst 1 / Day 1 inputs
        self.ip_inputs = []   # Analyst 2 / Day 2 inputs
        
        self.build_ui()
        self.load_project_data()

    def load_project_data(self):
        """Loads and displays current project metadata."""
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))

    def build_ui(self):
        self.setWindowTitle("Precision Validation Module")
        self.resize(1100, 850)
        self.setMinimumWidth(950)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area for clean viewing
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)

        # Central Container inside Scroll Area
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(container)

        # Text Styles
        title_style = "font-size:24px; font-weight:bold; color:#1A252C;"
        section_style = "font-size:16px; font-weight:bold; color:#2C3E50; margin-top:10px;"

        # =====================================================
        # Header Section
        # =====================================================
        title = QLabel("Precision Validation Workspace")
        title.setStyleSheet(title_style)
        scroll_layout.addWidget(title)

        # =====================================================
        # Project Info Block
        # =====================================================
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

        # =====================================================
        # Two-Column Columns for Repeatability & Intermediate Precision
        # =====================================================
        precision_columns = QHBoxLayout()
        precision_columns.setSpacing(20)

        # --- COLUMN 1: Repeatability (Analyst 1 / Day 1) ---
        rep_frame = QFrame()
        rep_frame.setFrameShape(QFrame.StyledPanel)
        rep_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;")
        rep_layout = QVBoxLayout(rep_frame)
        rep_layout.setSpacing(10)

        rep_title = QLabel("Repeatability (Method Precision)")
        rep_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1E3A8A; border-bottom: 2px solid #3B82F6; padding-bottom: 5px;")
        rep_layout.addWidget(rep_title)

        rep_subtitle = QLabel("Analyst 1 - Day 1 - Instrument 1")
        rep_subtitle.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        rep_layout.addWidget(rep_subtitle)

        rep_grid = QGridLayout()
        rep_grid.setSpacing(8)
        rep_grid.addWidget(QLabel("<b>Replicate</b>"), 0, 0)
        rep_grid.addWidget(QLabel("<b>Assay Result (%) / Area</b>"), 0, 1)

        for i in range(6):
            lbl = QLabel(f"Replicate {i+1}:")
            txt = QLineEdit()
            txt.setPlaceholderText("0.00")
            txt.setAlignment(Qt.AlignRight)
            txt.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
            txt.textChanged.connect(self.update_calculations)
            self.rep_inputs.append(txt)
            rep_grid.addWidget(lbl, i+1, 0)
            rep_grid.addWidget(txt, i+1, 1)
        
        rep_layout.addLayout(rep_grid)

        # Repeatability Summary
        rep_summary_layout = QGridLayout()
        rep_summary_layout.setSpacing(8)
        self.lblRepMean = QLabel("0.00%")
        self.lblRepSD = QLabel("0.0000")
        self.lblRepRSD = QLabel("0.00%")
        self.lblRepStatus = QLabel("Pending")
        self.lblRepStatus.setStyleSheet("font-weight: bold; color: gray;")

        rep_summary_layout.addWidget(QLabel("<b>Mean:</b>"), 0, 0)
        rep_summary_layout.addWidget(self.lblRepMean, 0, 1)
        rep_summary_layout.addWidget(QLabel("<b>SD:</b>"), 0, 2)
        rep_summary_layout.addWidget(self.lblRepSD, 0, 3)
        rep_summary_layout.addWidget(QLabel("<b>% RSD:</b>"), 1, 0)
        rep_summary_layout.addWidget(self.lblRepRSD, 1, 1)
        rep_summary_layout.addWidget(QLabel("<b>Status:</b>"), 1, 2)
        rep_summary_layout.addWidget(self.lblRepStatus, 1, 3)

        rep_layout.addLayout(rep_summary_layout)
        precision_columns.addWidget(rep_frame, 1)

        # --- COLUMN 2: Intermediate Precision (Analyst 2 / Day 2) ---
        ip_frame = QFrame()
        ip_frame.setFrameShape(QFrame.StyledPanel)
        ip_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;")
        ip_layout = QVBoxLayout(ip_frame)
        ip_layout.setSpacing(10)

        ip_title = QLabel("Intermediate Precision")
        ip_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1E3A8A; border-bottom: 2px solid #10B981; padding-bottom: 5px;")
        ip_layout.addWidget(ip_title)

        ip_subtitle = QLabel("Analyst 2 - Day 2 - Instrument 2 (Optional)")
        ip_subtitle.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        ip_layout.addWidget(ip_subtitle)

        ip_grid = QGridLayout()
        ip_grid.setSpacing(8)
        ip_grid.addWidget(QLabel("<b>Replicate</b>"), 0, 0)
        ip_grid.addWidget(QLabel("<b>Assay Result (%) / Area</b>"), 0, 1)

        for i in range(6):
            lbl = QLabel(f"Replicate {i+1}:")
            txt = QLineEdit()
            txt.setPlaceholderText("0.00")
            txt.setAlignment(Qt.AlignRight)
            txt.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
            txt.textChanged.connect(self.update_calculations)
            self.ip_inputs.append(txt)
            ip_grid.addWidget(lbl, i+1, 0)
            ip_grid.addWidget(txt, i+1, 1)

        ip_layout.addLayout(ip_grid)

        # Intermediate Precision Summary
        ip_summary_layout = QGridLayout()
        ip_summary_layout.setSpacing(8)
        self.lblIpMean = QLabel("0.00%")
        self.lblIpSD = QLabel("0.0000")
        self.lblIpRSD = QLabel("0.00%")
        self.lblIpStatus = QLabel("Pending")
        self.lblIpStatus.setStyleSheet("font-weight: bold; color: gray;")

        ip_summary_layout.addWidget(QLabel("<b>Mean:</b>"), 0, 0)
        ip_summary_layout.addWidget(self.lblIpMean, 0, 1)
        ip_summary_layout.addWidget(QLabel("<b>SD:</b>"), 0, 2)
        ip_summary_layout.addWidget(self.lblIpSD, 0, 3)
        ip_summary_layout.addWidget(QLabel("<b>% RSD:</b>"), 1, 0)
        ip_summary_layout.addWidget(self.lblIpRSD, 1, 1)
        ip_summary_layout.addWidget(QLabel("<b>Status:</b>"), 1, 2)
        ip_summary_layout.addWidget(self.lblIpStatus, 1, 3)

        ip_layout.addLayout(ip_summary_layout)
        precision_columns.addWidget(ip_frame, 1)

        scroll_layout.addLayout(precision_columns)

        # =====================================================
        # Combined Ruggedness / Precision Summary Block
        # =====================================================
        combined_header = QLabel("Combined Precision Analysis")
        combined_header.setStyleSheet(section_style)
        scroll_layout.addWidget(combined_header)

        combinedFrame = QFrame()
        combinedFrame.setFrameShape(QFrame.StyledPanel)
        combinedFrame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        combinedLayout = QGridLayout(combinedFrame)
        combinedLayout.setContentsMargins(15, 15, 15, 15)
        combinedLayout.setSpacing(15)

        self.lblCombMean = QLabel("0.00%")
        self.lblCombRSD = QLabel("0.00%")
        self.lblCombSD = QLabel("0.0000")
        self.lblOverallStatus = QLabel("Pending")
        self.lblOverallStatus.setStyleSheet("color: gray; font-weight: bold; font-size: 14px;")

        combinedLayout.addWidget(QLabel("<b>Combined Mean (N=12):</b>"), 0, 0)
        combinedLayout.addWidget(self.lblCombMean, 0, 1)
        combinedLayout.addWidget(QLabel("<b>Pooled Standard Deviation (SD):</b>"), 0, 2)
        combinedLayout.addWidget(self.lblCombSD, 0, 3)
        combinedLayout.addWidget(QLabel("<b>Combined % RSD:</b>"), 1, 0)
        combinedLayout.addWidget(self.lblCombRSD, 1, 1)
        combinedLayout.addWidget(QLabel("<b>Overall Validation Status:</b>"), 1, 2)
        combinedLayout.addWidget(self.lblOverallStatus, 1, 3)

        scroll_layout.addWidget(combinedFrame)

        # =====================================================
        # Two-Sample T-Test (Equal Variance)
        # =====================================================
        ttest_header = QLabel("Statistical T-Test (Two Samples, Equal Variance)")
        ttest_header.setStyleSheet(section_style)
        scroll_layout.addWidget(ttest_header)

        ttestFrame = QFrame()
        ttestFrame.setFrameShape(QFrame.StyledPanel)
        ttestFrame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        ttestLayout = QGridLayout(ttestFrame)
        ttestLayout.setContentsMargins(15, 15, 15, 15)
        ttestLayout.setSpacing(15)

        ttest_note = QLabel(
            "Compares Repeatability (Sample 1) vs Intermediate Precision (Sample 2) "
            "using a pooled-variance two-sample t-test."
        )
        ttest_note.setStyleSheet("color: #64748B; font-size: 11px; font-style: italic;")
        ttest_note.setWordWrap(True)
        ttestLayout.addWidget(ttest_note, 0, 0, 1, 4)

        self.lblTStat = QLabel("—")
        self.lblPValue = QLabel("—")
        self.lblAlpha = QLabel(f"{self.ALPHA:.2f}")
        self.lblTTestDF = QLabel("—")
        self.lblTTestStatus = QLabel("Pending")
        self.lblTTestStatus.setStyleSheet("color: gray; font-weight: bold;")

        ttestLayout.addWidget(QLabel("<b>Alpha (α):</b>"), 1, 0)
        ttestLayout.addWidget(self.lblAlpha, 1, 1)
        ttestLayout.addWidget(QLabel("<b>Degrees of Freedom:</b>"), 1, 2)
        ttestLayout.addWidget(self.lblTTestDF, 1, 3)
        ttestLayout.addWidget(QLabel("<b>t-Statistic:</b>"), 2, 0)
        ttestLayout.addWidget(self.lblTStat, 2, 1)
        ttestLayout.addWidget(QLabel("<b>p-Value (Probability Factor):</b>"), 2, 2)
        ttestLayout.addWidget(self.lblPValue, 2, 3)
        ttestLayout.addWidget(QLabel("<b>T-Test Status (p ≤ α):</b>"), 3, 0)
        ttestLayout.addWidget(self.lblTTestStatus, 3, 1, 1, 3)

        scroll_layout.addWidget(ttestFrame)

        # =====================================================
        # Bottom Utility Actions Row
        # =====================================================
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btnSave = QPushButton("Save Precision Data")
        self.btnSave.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btnSave.clicked.connect(self.save_data)
        buttons_layout.addWidget(self.btnSave)
        scroll_layout.addLayout(buttons_layout)

    # =====================================================
    # Math Engine
    # =====================================================
    def get_inputs(self, input_list):
        vals = []
        for inp in input_list:
            try:
                if inp.text().strip():
                    vals.append(float(inp.text()))
            except ValueError:
                pass
        return vals

    def calculate_stats(self, values):
        if not values:
            return 0.0, 0.0, 0.0
        
        mean = sum(values) / len(values)
        sd = 0.0
        if len(values) >= 2:
            variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
            sd = math.sqrt(variance)
        
        rsd = (sd / mean) * 100 if mean > 0 else 0.0
        return mean, sd, rsd

    def run_ttest(self, rep_vals, ip_vals):
        """Runs two-sample t-test when both sample sets are complete."""
        if len(rep_vals) == 6 and len(ip_vals) == 6:
            return PrecisionCalculator.two_sample_ttest_equal_variance(
                rep_vals, ip_vals, alpha=self.ALPHA
            )
        return {
            "t_statistic": None,
            "p_value": None,
            "df": None,
            "pooled_sd": None,
            "alpha": self.ALPHA,
            "status": "PENDING",
        }

    def _set_status_label(self, label, status):
        styles = {
            "PASS": "color: green; font-weight: bold;",
            "FAIL": "color: red; font-weight: bold;",
            "PENDING": "color: gray; font-weight: bold;",
            "Incomplete (Need 6)": "color: orange; font-weight: bold;",
            "Pending Data": "color: gray; font-weight: bold;",
            "N/A": "color: #94A3B8; font-weight: bold;",
        }
        label.setText(status)
        label.setStyleSheet(styles.get(status, "color: gray; font-weight: bold;"))

    def _update_ttest_display(self, ttest):
        if ttest["t_statistic"] is None:
            self.lblTStat.setText("—")
            self.lblPValue.setText("—")
            self.lblTTestDF.setText("—")
            if ttest["status"] == "PENDING":
                self._set_status_label(self.lblTTestStatus, "N/A (Need both samples)")
            else:
                self._set_status_label(self.lblTTestStatus, "PENDING")
            return

        self.lblTStat.setText(f"{ttest['t_statistic']:.4f}")
        self.lblPValue.setText(f"{ttest['p_value']:.4f}")
        self.lblTTestDF.setText(str(ttest["df"]))
        self._set_status_label(self.lblTTestStatus, ttest["status"])

    def _determine_overall_status(self, rep_vals, ip_vals, rep_rsd, comb_rsd, ttest_status):
        rep_complete = len(rep_vals) == 6
        ip_complete = len(ip_vals) == 6
        ip_entered = len(ip_vals) > 0

        if not rep_complete:
            return "Pending Data"

        rep_pass = rep_rsd <= 2.0
        ip_pass = len(ip_vals) == 6 and self.calculate_stats(ip_vals)[2] <= 2.0
        comb_pass = comb_rsd <= 2.0 if ip_complete else True

        if ip_complete:
            ttest_pass = ttest_status == "PASS"
            if rep_pass and ip_pass and comb_pass and ttest_pass:
                return "PASS"
            if rep_pass and ip_pass and comb_pass and ttest_status == "PENDING":
                return "Pending Data"
            return "FAIL"

        if ip_entered and not ip_complete:
            return "Pending Data"

        return "PASS" if rep_pass else "FAIL"

    def update_calculations(self):
        """Live updates stats as values are typed."""
        # 1. Repeatability Calculations (Analyst 1)
        rep_vals = self.get_inputs(self.rep_inputs)
        rep_mean, rep_sd, rep_rsd = self.calculate_stats(rep_vals)

        if len(rep_vals) > 0:
            self.lblRepMean.setText(f"{rep_mean:.2f}%" if rep_mean <= 200 else f"{rep_mean:.2f}")
            self.lblRepSD.setText(f"{rep_sd:.4f}")
            self.lblRepRSD.setText(f"{rep_rsd:.2f}%")
            
            # Acceptance Criteria: Typically %RSD <= 2.0% for method precision
            if len(rep_vals) == 6:
                self._set_status_label(
                    self.lblRepStatus, "PASS" if rep_rsd <= 2.0 else "FAIL"
                )
            else:
                self._set_status_label(self.lblRepStatus, "Incomplete (Need 6)")
        else:
            self.lblRepMean.setText("0.00%")
            self.lblRepSD.setText("0.0000")
            self.lblRepRSD.setText("0.00%")
            self._set_status_label(self.lblRepStatus, "PENDING")

        # 2. Intermediate Precision Calculations (Analyst 2)
        ip_vals = self.get_inputs(self.ip_inputs)
        ip_mean, ip_sd, ip_rsd = self.calculate_stats(ip_vals)

        if len(ip_vals) > 0:
            self.lblIpMean.setText(f"{ip_mean:.2f}%" if ip_mean <= 200 else f"{ip_mean:.2f}")
            self.lblIpSD.setText(f"{ip_sd:.4f}")
            self.lblIpRSD.setText(f"{ip_rsd:.2f}%")
            
            if len(ip_vals) == 6:
                self._set_status_label(
                    self.lblIpStatus, "PASS" if ip_rsd <= 2.0 else "FAIL"
                )
            else:
                self._set_status_label(self.lblIpStatus, "Incomplete (Need 6)")
        else:
            self.lblIpMean.setText("0.00%")
            self.lblIpSD.setText("0.0000")
            self.lblIpRSD.setText("0.00%")
            self._set_status_label(self.lblIpStatus, "PENDING")

        # 3. Combined Precision Calculations (Analyst 1 + Analyst 2 combined)
        combined_vals = rep_vals + ip_vals
        comb_mean, comb_sd, comb_rsd = self.calculate_stats(combined_vals)
        ttest = self.run_ttest(rep_vals, ip_vals)
        self._update_ttest_display(ttest)

        if len(combined_vals) > 0:
            self.lblCombMean.setText(f"{comb_mean:.2f}%" if comb_mean <= 200 else f"{comb_mean:.2f}")
            self.lblCombSD.setText(f"{comb_sd:.4f}")
            self.lblCombRSD.setText(f"{comb_rsd:.2f}%")

            overall = self._determine_overall_status(
                rep_vals, ip_vals, rep_rsd, comb_rsd, ttest["status"]
            )
            self._set_status_label(self.lblOverallStatus, overall)
            if overall in ("PASS", "FAIL"):
                self.lblOverallStatus.setStyleSheet(
                    self.lblOverallStatus.styleSheet() + " font-size: 14px;"
                )
        else:
            self.lblCombMean.setText("0.00%")
            self.lblCombSD.setText("0.0000")
            self.lblCombRSD.setText("0.00%")
            self._set_status_label(self.lblOverallStatus, "PENDING")
            self.lblOverallStatus.setStyleSheet(
                "color: gray; font-weight: bold; font-size: 14px;"
            )

    def save_data(self):
        """Saves precision validation data to database."""
        # Collect all input values
        rep_vals = self.get_inputs(self.rep_inputs)
        ip_vals = self.get_inputs(self.ip_inputs)
        
        # Calculate statistics
        rep_mean, rep_sd, rep_rsd = self.calculate_stats(rep_vals)
        ip_mean, ip_sd, ip_rsd = self.calculate_stats(ip_vals)
        
        combined_vals = rep_vals + ip_vals
        comb_mean, comb_sd, comb_rsd = self.calculate_stats(combined_vals)
        ttest = self.run_ttest(rep_vals, ip_vals)
        
        # Determine status
        rep_status = "PASS" if len(rep_vals) == 6 and rep_rsd <= 2.0 else "FAIL" if len(rep_vals) == 6 else "PENDING"
        ip_status = "PASS" if len(ip_vals) == 6 and ip_rsd <= 2.0 else "FAIL" if len(ip_vals) == 6 else "PENDING"
        overall_status = self._determine_overall_status(
            rep_vals, ip_vals, rep_rsd, comb_rsd, ttest["status"]
        )
        if overall_status == "Pending Data":
            overall_status = "PENDING"
        
        if self.project and len(self.project) > 0:
            project_id = self.project[0]
            
            try:
                # Prepare data dictionary
                data = {
                    "rep_1": rep_vals[0] if len(rep_vals) > 0 else 0.0,
                    "rep_2": rep_vals[1] if len(rep_vals) > 1 else 0.0,
                    "rep_3": rep_vals[2] if len(rep_vals) > 2 else 0.0,
                    "rep_4": rep_vals[3] if len(rep_vals) > 3 else 0.0,
                    "rep_5": rep_vals[4] if len(rep_vals) > 4 else 0.0,
                    "rep_6": rep_vals[5] if len(rep_vals) > 5 else 0.0,
                    "rep_mean": rep_mean,
                    "rep_sd": rep_sd,
                    "rep_rsd": rep_rsd,
                    "rep_status": rep_status,
                    "ip_1": ip_vals[0] if len(ip_vals) > 0 else 0.0,
                    "ip_2": ip_vals[1] if len(ip_vals) > 1 else 0.0,
                    "ip_3": ip_vals[2] if len(ip_vals) > 2 else 0.0,
                    "ip_4": ip_vals[3] if len(ip_vals) > 3 else 0.0,
                    "ip_5": ip_vals[4] if len(ip_vals) > 4 else 0.0,
                    "ip_6": ip_vals[5] if len(ip_vals) > 5 else 0.0,
                    "ip_mean": ip_mean,
                    "ip_sd": ip_sd,
                    "ip_rsd": ip_rsd,
                    "ip_status": ip_status,
                    "combined_mean": comb_mean,
                    "combined_sd": comb_sd,
                    "combined_rsd": comb_rsd,
                    "overall_status": overall_status,
                    "t_statistic": ttest["t_statistic"],
                    "t_p_value": ttest["p_value"],
                    "t_alpha": ttest["alpha"],
                    "t_test_status": ttest["status"],
                }
                
                # Save to database
                save_precision(project_id, data)
                _update_summary_status(project_id, "precision_status", overall_status)
                update_overall_status(project_id)
                
                QMessageBox.information(
                    self,
                    "Validation Saved",
                    f"Precision validation results saved successfully!\n\n"
                    f"Repeatability Mean: {rep_mean:.2f}%, RSD: {rep_rsd:.2f}%, Status: {rep_status}\n"
                    f"Intermediate Precision Mean: {ip_mean:.2f}%, RSD: {ip_rsd:.2f}%, Status: {ip_status}\n"
                    f"Combined Mean: {comb_mean:.2f}%, RSD: {comb_rsd:.2f}%\n"
                    f"T-Test p-Value: {ttest['p_value'] if ttest['p_value'] is not None else 'N/A'}, "
                    f"Status: {ttest['status']}\n"
                    f"Overall Status: {overall_status}",
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"An error occurred while saving: {e}",
                    QMessageBox.Ok
                )
        else:
            QMessageBox.warning(
                self,
                "No Active Project",
                "Cannot save because no active validation project ID was found.",
                QMessageBox.Ok
            )