import math
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

# Dynamic fallback path handling to safely locate root modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.recovery_level import RecoveryLevelWidget

# Import exact matching database synchronization layout from package layer
from database.database import save_accuracy, _update_summary_status, update_overall_status


class AccuracyWindow(QWidget):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.sst_inputs = []
        self.current_db_payload = {}  # Cache payload in memory for when they click save
        self.build_ui()
        self.load_project_data()

    def load_project_data(self):
        """Safely loads and displays the metadata of the current project."""
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))

    def build_ui(self):
        self.setWindowTitle("Accuracy Validation Module")
        self.resize(1100, 850)
        self.setMinimumWidth(950)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        window_layout.addWidget(scroll_area)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(container)

        title_style = "font-size:24px; font-weight:bold; color:#1A252C;"
        section_style = "font-size:16px; font-weight:bold; color:#2C3E50; margin-top:10px;"

        # =====================================================
        # Header Section
        # =====================================================
        title = QLabel("Accuracy Validation Workspace")
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
        # Reference Configurations & SST Block
        # =====================================================
        config_and_sst = QHBoxLayout()
        config_and_sst.setSpacing(15)

        ref_frame = QFrame()
        ref_frame.setFrameShape(QFrame.StyledPanel)
        ref_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px;")
        ref_layout = QGridLayout(ref_frame)
        ref_layout.setSpacing(10)

        ref_title = QLabel("Reference Standards & Blank Configuration")
        ref_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E3A8A;")
        ref_layout.addWidget(ref_title, 0, 0, 1, 2)

        ref_layout.addWidget(QLabel("Global Matrix/Placebo Response (Area):"), 1, 0)
        self.txtGlobalMatrix = QLineEdit("0.0")
        self.txtGlobalMatrix.setAlignment(Qt.AlignRight)
        self.txtGlobalMatrix.textChanged.connect(self.update_calculations)
        ref_layout.addWidget(self.txtGlobalMatrix, 1, 1)

        ref_layout.addWidget(QLabel("Standard Weight Spiked (mg):"), 2, 0)
        self.txtStdWeight = QLineEdit("10.0")
        self.txtStdWeight.setAlignment(Qt.AlignRight)
        self.txtStdWeight.textChanged.connect(self.update_calculations)
        ref_layout.addWidget(self.txtStdWeight, 2, 1)

        ref_layout.addWidget(QLabel("Dilution Factor / Multiplier:"), 3, 0)
        self.txtDilutionRatio = QLineEdit("1.0")
        self.txtDilutionRatio.setAlignment(Qt.AlignRight)
        self.txtDilutionRatio.textChanged.connect(self.update_calculations)
        ref_layout.addWidget(self.txtDilutionRatio, 3, 1)

        config_and_sst.addWidget(ref_frame, 1)

        sstFrame = QFrame()
        sstFrame.setFrameShape(QFrame.StyledPanel)
        sstFrame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px;")
        sstLayout = QGridLayout(sstFrame)
        sstLayout.setSpacing(8)

        sst_title = QLabel("System Suitability Test (Standard Injections)")
        sst_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E3A8A;")
        sstLayout.addWidget(sst_title, 0, 0, 1, 4)

        for i in range(5):
            lbl = QLabel(f"Inj {i + 1}:")
            txt = QLineEdit()
            txt.setPlaceholderText("0.0")
            txt.setAlignment(Qt.AlignRight)
            txt.textChanged.connect(self.update_calculations)
            self.sst_inputs.append(txt)
            sstLayout.addWidget(lbl, (i % 3) + 1, 0 if i < 3 else 2)
            sstLayout.addWidget(txt, (i % 3) + 1, 1 if i < 3 else 3)

        self.lblMean = QLabel("0.00")
        self.lblRSD = QLabel("0.00%")
        
        sstLayout.addWidget(QLabel("<b>Mean Area:</b>"), 4, 0)
        sstLayout.addWidget(self.lblMean, 4, 1)
        sstLayout.addWidget(QLabel("<b>% RSD (N=5):</b>"), 4, 2)
        sstLayout.addWidget(self.lblRSD, 4, 3)

        config_and_sst.addWidget(sstFrame, 1)
        scroll_layout.addLayout(config_and_sst)

        # =====================================================
        # Recovery Levels
        # =====================================================
        recovery_header = QLabel("Level-Specific Recovery Analyses")
        recovery_header.setStyleSheet(section_style)
        scroll_layout.addWidget(recovery_header)

        self.level80 = RecoveryLevelWidget(80)
        self.level100 = RecoveryLevelWidget(100)
        self.level120 = RecoveryLevelWidget(120)

        scroll_layout.addWidget(self.level80)
        scroll_layout.addWidget(self.level100)
        scroll_layout.addWidget(self.level120)

        self.connect_level_events(self.level80)
        self.connect_level_events(self.level100)
        self.connect_level_events(self.level120)

        # =====================================================
        # Overall Summary Section
        # =====================================================
        summary_title = QLabel("Overall Validation Summary")
        summary_title.setStyleSheet(section_style)
        scroll_layout.addWidget(summary_title)

        summaryFrame = QFrame()
        summaryFrame.setFrameShape(QFrame.StyledPanel)
        summaryFrame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        summaryLayout = QGridLayout(summaryFrame)
        summaryLayout.setContentsMargins(15, 15, 15, 15)
        summaryLayout.setSpacing(15)

        self.lblOverallRecovery = QLabel("0.00%")
        self.lblOverallRSD = QLabel("0.00%")
        self.lblOverallBias = QLabel("0.00%")
        self.lblPooledSD = QLabel("0.0000")
        self.lblStatus = QLabel("Pending")
        self.lblStatus.setStyleSheet("color: gray; font-weight: bold; font-size: 14px;")

        summaryLayout.addWidget(QLabel("<b>Overall Mean Recovery (80% - 120%):</b>"), 0, 0)
        summaryLayout.addWidget(self.lblOverallRecovery, 0, 1)
        summaryLayout.addWidget(QLabel("<b>Pooled Standard Deviation (SD):</b>"), 0, 2)
        summaryLayout.addWidget(self.lblPooledSD, 0, 3)
        summaryLayout.addWidget(QLabel("<b>Overall % RSD:</b>"), 1, 0)
        summaryLayout.addWidget(self.lblOverallRSD, 1, 1)
        summaryLayout.addWidget(QLabel("<b>Overall % Bias:</b>"), 1, 2)
        summaryLayout.addWidget(self.lblOverallBias, 1, 3)
        summaryLayout.addWidget(QLabel("<b>Final Module Validation Status:</b>"), 2, 0)
        summaryLayout.addWidget(self.lblStatus, 2, 1)

        scroll_layout.addWidget(summaryFrame)

        # =====================================================
        # Bottom Utility Actions Row
        # =====================================================
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btnSaveData = QPushButton("Save Accuracy Data")
        self.btnSaveData.setStyleSheet("""
            QPushButton {
                background-color: #16A34A;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #15803D;
            }
        """)
        self.btnSaveData.clicked.connect(self.handle_save_button_click)
        buttons_layout.addWidget(self.btnSaveData)
        scroll_layout.addLayout(buttons_layout)

    def connect_level_events(self, level_widget):
        for spike_input in level_widget.spike_inputs:
            spike_input.textChanged.connect(self.update_calculations)
        for added_input in level_widget.added_inputs:
            added_input.textChanged.connect(self.update_calculations)

    def get_sst_values(self):
        vals = []
        for inp in self.sst_inputs:
            try:
                if inp.text().strip():
                    vals.append(float(inp.text()))
                else:
                    vals.append(0.0)
            except ValueError:
                vals.append(0.0)
        return vals

    def update_calculations(self):
        """Centralized calculation engine. Updates UI immediately but does NOT touch the database."""
        sst_vals = self.get_sst_values()
        while len(sst_vals) < 5:
            sst_vals.append(0.0)

        valid_sst = [v for v in sst_vals if v > 0]
        mean_sst = 0.0
        rsd_sst = 0.0
        
        if len(valid_sst) >= 1:
            mean_sst = sum(valid_sst) / len(valid_sst)
            self.lblMean.setText(f"{mean_sst:.2f}")
        else:
            self.lblMean.setText("0.00")

        if len(valid_sst) >= 2:
            variance = sum((x - mean_sst) ** 2 for x in valid_sst) / (len(valid_sst) - 1)
            sd_sst = math.sqrt(variance)
            rsd_sst = (sd_sst / mean_sst) * 100 if mean_sst > 0 else 0.0
            self.lblRSD.setText(f"{rsd_sst:.2f}%")
        else:
            self.lblRSD.setText("0.00%")

        try:
            matrix_response = float(self.txtGlobalMatrix.text()) if self.txtGlobalMatrix.text().strip() else 0.0
        except ValueError:
            matrix_response = 0.0

        try:
            std_weight = float(self.txtStdWeight.text()) if self.txtStdWeight.text().strip() else 10.0
        except ValueError:
            std_weight = 10.0

        try:
            dilution_ratio = float(self.txtDilutionRatio.text()) if self.txtDilutionRatio.text().strip() else 1.0
        except ValueError:
            dilution_ratio = 1.0

        all_level_recoveries = []
        groups_for_pooling = []
        
        # Build the payload dictionary structure in memory
        self.current_db_payload = {
            "sst_1": sst_vals[0], "sst_2": sst_vals[1], "sst_3": sst_vals[2],
            "sst_4": sst_vals[3], "sst_5": sst_vals[4],
            "sst_mean": mean_sst, "sst_rsd": rsd_sst,
            "matrix_response": matrix_response, "std_weight": std_weight, "dilution_ratio": dilution_ratio
        }

        level_prefixes = {self.level80: "l80", self.level100: "l100", self.level120: "l120"}

        for widget, prefix in level_prefixes.items():
            spikes = widget.spike_values()
            addeds = widget.added_values()
            recoveries = []

            for i in range(widget.replicates):
                spk = spikes[i] if i < len(spikes) else 0.0
                add_mg = addeds[i] if i < len(addeds) else 0.0

                net_response = max(0.0, spk - matrix_response) if spk > 0 else 0.0
                recovered_mg = 0.0
                if mean_sst > 0 and net_response > 0:
                    recovered_mg = (net_response / mean_sst) * std_weight * dilution_ratio

                pct_rec = 0.0
                if add_mg > 0:
                    pct_rec = (recovered_mg / add_mg) * 100.0

                widget.set_replicate_outputs(i, net_response, recovered_mg, pct_rec)

                self.current_db_payload[f"{prefix}_spike_{i+1}"] = spk
                self.current_db_payload[f"{prefix}_found_{i+1}"] = recovered_mg
                self.current_db_payload[f"{prefix}_rec_{i+1}"] = pct_rec

                if spk > 0 and add_mg > 0:
                    recoveries.append(pct_rec)
                    all_level_recoveries.append(pct_rec)

            if len(recoveries) > 0:
                groups_for_pooling.append(recoveries)
                level_mean = sum(recoveries) / len(recoveries)
                
                level_rsd = 0.0
                if len(recoveries) >= 2:
                    var = sum((x - level_mean) ** 2 for x in recoveries) / (len(recoveries) - 1)
                    level_rsd = (math.sqrt(var) / level_mean) * 100 if level_mean > 0 else 0.0
                
                level_bias = level_mean - 100.0
                status = "PASS" if level_rsd <= 2.0 and (98.0 <= level_mean <= 102.0) else "FAIL"
                widget.set_summary(level_mean, level_rsd, level_bias, status)
                
                self.current_db_payload[f"{prefix}_mean"] = level_mean
                self.current_db_payload[f"{prefix}_rsd"] = level_rsd
                self.current_db_payload[f"{prefix}_bias"] = level_bias
                self.current_db_payload[f"{prefix}_status"] = status
            else:
                widget.set_summary(0.0, 0.0, 0.0, "Pending")
                self.current_db_payload[f"{prefix}_mean"] = 0.0
                self.current_db_payload[f"{prefix}_rsd"] = 0.0
                self.current_db_payload[f"{prefix}_bias"] = 0.0
                self.current_db_payload[f"{prefix}_status"] = "PENDING"

        final_status = "PENDING"
        overall_mean = 0.0
        overall_rsd = 0.0
        overall_bias = 0.0
        pooled_sd = 0.0

        if len(all_level_recoveries) > 0:
            overall_mean = sum(all_level_recoveries) / len(all_level_recoveries)
            if len(all_level_recoveries) >= 2:
                o_var = sum((x - overall_mean) ** 2 for x in all_level_recoveries) / (len(all_level_recoveries) - 1)
                overall_rsd = (math.sqrt(o_var) / overall_mean) * 100 if overall_mean > 0 else 0.0

            overall_bias = overall_mean - 100.0

            total_variance = 0.0
            total_df = 0
            for gp in groups_for_pooling:
                if len(gp) >= 2:
                    gp_mean = sum(gp) / len(gp)
                    gp_var = sum((x - gp_mean) ** 2 for x in gp) / (len(gp) - 1)
                    total_variance += gp_var * (len(gp) - 1)
                    total_df += (len(gp) - 1)

            if total_df > 0:
                pooled_sd = math.sqrt(total_variance / total_df)

            self.lblOverallRecovery.setText(f"{overall_mean:.2f}%")
            self.lblOverallRSD.setText(f"{overall_rsd:.2f}%")
            self.lblOverallBias.setText(f"{overall_bias:.2f}%")
            self.lblPooledSD.setText(f"{pooled_sd:.4f}")

            if 98.0 <= overall_mean <= 102.0 and overall_rsd <= 2.0:
                final_status = "PASS"
                self.lblStatus.setText("PASS")
                self.lblStatus.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            else:
                final_status = "FAIL"
                self.lblStatus.setText("FAIL")
                self.lblStatus.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        else:
            self.lblOverallRecovery.setText("0.00%")
            self.lblOverallRSD.setText("0.00%")
            self.lblOverallBias.setText("0.00%")
            self.lblPooledSD.setText("0.0000")
            self.lblStatus.setText("Pending")
            self.lblStatus.setStyleSheet("color: gray; font-weight: bold; font-size: 14px;")

        self.current_db_payload["overall_mean"] = overall_mean
        self.current_db_payload["overall_rsd"] = overall_rsd
        self.current_db_payload["overall_bias"] = overall_bias
        self.current_db_payload["pooled_sd"] = pooled_sd
        self.current_db_payload["overall_status"] = final_status

    def handle_save_button_click(self):
        """Processes the exact SQLite commits ONLY when the user clicks save."""
        # Ensure latest user keystrokes are integrated right before committing
        self.update_calculations()

        if self.project and len(self.project) > 0:
            try:
                project_id = self.project[0]
                final_status = self.current_db_payload.get("overall_status", "PENDING")
                
                # Execute database write pipeline now
                save_accuracy(project_id, self.current_db_payload)
                _update_summary_status(project_id, "accuracy_status", final_status)
                update_overall_status(project_id)
                
                # Pop confirmation box to user
                QMessageBox.information(
                    self,
                    "Validation Module Saved",
                    "Accuracy validation metrics and level-specific data sets have been successfully saved to the project log database.",
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"An error occurred while writing to the database: {e}",
                    QMessageBox.Ok
                )
        else:
            QMessageBox.warning(
                self,
                "No Active Project",
                "Cannot save because no active validation project ID was found.",
                QMessageBox.Ok
            )