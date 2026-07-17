"""
PharmaValidate v0.5 - Specificity Validation Module
Evaluates interference of Blank, Placebo, and Excipients at Active RT,
and verifies peak resolution (Rs >= 1.5).
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
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class SpecificityWindow(QWidget):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.rows_data = []  # List of dicts storing row widgets
        
        self.build_ui()
        self.load_project_data()
        self.add_default_rows()

    def load_project_data(self):
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))

    def build_ui(self):
        self.setWindowTitle("Specificity Validation Module")
        self.resize(1150, 750)
        self.setMinimumWidth(950)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(container)

        # Title
        title = QLabel("Specificity Validation Workspace")
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#0F172A;")
        scroll_layout.addWidget(title)

        # Project Metadata
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

        # Main Workspace Panel
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;")
        content_layout = QVBoxLayout(content_frame)
        
        table_header = QLabel("Chromatographic Injection Performance Grid")
        table_header.setStyleSheet("font-weight: bold; font-size: 15px; color: #1E3A8A; border-bottom: 2px solid #3B82F6; padding-bottom: 5px;")
        content_layout.addWidget(table_header)

        # Grid Header Labels
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setContentsMargins(0, 10, 0, 10)
        
        headers = [
            "Injection Matrix / Sample Type", 
            "Peak Detected?", 
            "Retention Time (Rt, min)", 
            "Peak Area", 
            "Resolution (Rs)", 
            "Interference (%)", 
            "Compendial Status"
        ]
        
        for col, text in enumerate(headers):
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            lbl.setStyleSheet("background-color: #F1F5F9; padding: 6px; border-radius: 4px; font-size: 11px;")
            self.grid_layout.addWidget(lbl, 0, col)

        content_layout.addWidget(self.grid_widget)
        
        # Add Custom Entry Row Button
        btn_add_row = QPushButton("+ Add Custom Chromatographic Run")
        btn_add_row.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #475569; font-weight: bold; border: 1px dashed #CBD5E1; padding: 8px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_add_row.clicked.connect(self.add_custom_row)
        content_layout.addWidget(btn_add_row)
        
        scroll_layout.addWidget(content_frame)

        # Summary Block
        summary_header = QLabel("Specificity Validation Verdict")
        summary_header.setStyleSheet("font-size:16px; font-weight:bold; color:#2C3E50; margin-top:10px;")
        scroll_layout.addWidget(summary_header)

        summaryFrame = QFrame()
        summaryFrame.setFrameShape(QFrame.StyledPanel)
        summaryFrame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E2E8F0; border-radius: 8px;")
        summaryLayout = QGridLayout(summaryFrame)
        summaryLayout.setContentsMargins(15, 15, 15, 15)
        summaryLayout.setSpacing(15)

        self.lblMaxInterference = QLabel("0.00%")
        self.lblMinResolution = QLabel("N/A")
        self.lblOverallStatus = QLabel("Pending Data")
        self.lblOverallStatus.setStyleSheet("font-weight: bold; color: gray; font-size: 14px;")

        summaryLayout.addWidget(QLabel("<b>Max Placebo Interference at Active Rt:</b>"), 0, 0)
        summaryLayout.addWidget(self.lblMaxInterference, 0, 1)
        summaryLayout.addWidget(QLabel("<b>Minimum Resolution (Rs) observed:</b>"), 0, 2)
        summaryLayout.addWidget(self.lblMinResolution, 0, 3)
        summaryLayout.addWidget(QLabel("<b>Overall Specificity Verdict:</b>"), 1, 0)
        summaryLayout.addWidget(self.lblOverallStatus, 1, 1, 1, 3)

        scroll_layout.addWidget(summaryFrame)

        # Save Button
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        self.btnSave = QPushButton("💾 Save Specificity Data")
        self.btnSave.setStyleSheet("""
            QPushButton { 
                background-color: #10B981; 
                color: white; 
                font-weight: bold; 
                padding: 10px 20px; 
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btnSave.clicked.connect(self.save_data)
        actions_layout.addWidget(self.btnSave)
        scroll_layout.addLayout(actions_layout)

    def add_default_rows(self):
        # Traditional Chromatographic runs for standard pharmaceutical validation
        defaults = [
            ("Blank Diluent", "No", "", "", "", "0.00"),
            ("Placebo Solution (Excipients)", "No", "", "", "", "0.00"),
            ("Active Standard (Target API)", "Yes", "4.50", "1250450", "N/A", "0.00"),
            ("Assay Sample Solution", "Yes", "4.51", "1248900", "2.10", "0.00"),
        ]
        for item in defaults:
            self.create_row_inputs(item[0], item[1], item[2], item[3], item[4], item[5])

    def add_custom_row(self):
        self.create_row_inputs("Impurity / Degradant Mixture", "Yes", "", "", "", "0.00")

    def create_row_inputs(self, name, peak_detect, rt, area, rs, interference):
        row_idx = len(self.rows_data) + 1  # offset due to header
        
        # Widgets
        txt_name = QLineEdit(name)
        txt_name.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        
        combo_peak = QComboBox()
        combo_peak.addItems(["Yes", "No"])
        combo_peak.setCurrentText(peak_detect)
        combo_peak.currentIndexChanged.connect(self.update_calculations)

        txt_rt = QLineEdit(rt)
        txt_rt.setPlaceholderText("0.00")
        txt_rt.setAlignment(Qt.AlignCenter)
        txt_rt.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_rt.textChanged.connect(self.update_calculations)

        txt_area = QLineEdit(area)
        txt_area.setPlaceholderText("0.00")
        txt_area.setAlignment(Qt.AlignRight)
        txt_area.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_area.textChanged.connect(self.update_calculations)

        txt_rs = QLineEdit(rs)
        txt_rs.setPlaceholderText("N/A")
        txt_rs.setAlignment(Qt.AlignCenter)
        txt_rs.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_rs.textChanged.connect(self.update_calculations)

        txt_interf = QLineEdit(interference)
        txt_interf.setPlaceholderText("0.00")
        txt_interf.setAlignment(Qt.AlignRight)
        txt_interf.setStyleSheet("padding: 4px; border: 1px solid #CBD5E1; border-radius: 4px;")
        txt_interf.textChanged.connect(self.update_calculations)

        lbl_status = QLabel("PASS")
        lbl_status.setAlignment(Qt.AlignCenter)
        lbl_status.setStyleSheet("font-weight: bold; color: green;")

        # Place in layout
        self.grid_layout.addWidget(txt_name, row_idx, 0)
        self.grid_layout.addWidget(combo_peak, row_idx, 1)
        self.grid_layout.addWidget(txt_rt, row_idx, 2)
        self.grid_layout.addWidget(txt_area, row_idx, 3)
        self.grid_layout.addWidget(txt_rs, row_idx, 4)
        self.grid_layout.addWidget(txt_interf, row_idx, 5)
        self.grid_layout.addWidget(lbl_status, row_idx, 6)

        self.rows_data.append({
            "name": txt_name,
            "peak_detected": combo_peak,
            "rt": txt_rt,
            "area": txt_area,
            "rs": txt_rs,
            "interference": txt_interf,
            "status": lbl_status
        })
        self.update_calculations()

    def update_calculations(self):
        """Processes validation parameters against USP/BP guidelines live."""
        max_interference = 0.0
        min_resolution = float('inf')
        all_passed = True

        # Extract Active API Standard Area as reference
        active_std_area = 1.0
        for r in self.rows_data:
            name_text = r["name"].text().lower()
            if "active" in name_text or "standard" in name_text:
                try:
                    active_std_area = float(r["area"].text()) if r["area"].text() else 1.0
                except ValueError:
                    pass

        for r in self.rows_data:
            name = r["name"].text().lower()
            peak_yes = r["peak_detected"].currentText() == "Yes"
            
            is_matrix = "blank" in name or "placebo" in name or "excipient" in name
            
            try:
                interf_val = float(r["interference"].text()) if r["interference"].text() else 0.0
            except ValueError:
                interf_val = 0.0

            if is_matrix:
                if peak_yes:
                    try:
                        area_val = float(r["area"].text()) if r["area"].text() else 0.0
                        if active_std_area > 1.0 and area_val > 0:
                            interf_val = (area_val / active_std_area) * 100
                            r["interference"].setText(f"{interf_val:.3f}")
                    except ValueError:
                        pass
                    
                    if interf_val > 0.5:
                        r["status"].setText("FAIL (Interf)")
                        r["status"].setStyleSheet("color: red; font-weight: bold;")
                        all_passed = False
                    else:
                        r["status"].setText("PASS")
                        r["status"].setStyleSheet("color: green; font-weight: bold;")
                    max_interference = max(max_interference, interf_val)
                else:
                    r["status"].setText("PASS")
                    r["status"].setStyleSheet("color: green; font-weight: bold;")
                    r["interference"].setText("0.00")
            else:
                try:
                    rs_val_str = r["rs"].text().strip()
                    if rs_val_str and rs_val_str.lower() != "n/a":
                        rs_val = float(rs_val_str)
                        min_resolution = min(min_resolution, rs_val)
                        if rs_val < 1.5:
                            r["status"].setText("FAIL (Rs < 1.5)")
                            r["status"].setStyleSheet("color: red; font-weight: bold;")
                            all_passed = False
                        else:
                            r["status"].setText("PASS")
                            r["status"].setStyleSheet("color: green; font-weight: bold;")
                    else:
                        r["status"].setText("PASS")
                        r["status"].setStyleSheet("color: green; font-weight: bold;")
                except ValueError:
                    r["status"].setText("PASS")
                    r["status"].setStyleSheet("color: green; font-weight: bold;")

        # Update summary panel
        self.lblMaxInterference.setText(f"{max_interference:.3f}%")
        if min_resolution != float('inf'):
            self.lblMinResolution.setText(f"{min_resolution:.2f}")
            if min_resolution < 1.5:
                all_passed = False
        else:
            self.lblMinResolution.setText("N/A")

        if all_passed and len(self.rows_data) > 0:
            self.lblOverallStatus.setText("PASS - No placebo interference detected; Resolution meets USP requirements.")
            self.lblOverallStatus.setStyleSheet("color: green; font-weight: bold; font-size: 13px;")
        else:
            self.lblOverallStatus.setText("FAIL - Active peaks compromised by placebo interference or resolution < 1.5.")
            self.lblOverallStatus.setStyleSheet("color: red; font-weight: bold; font-size: 13px;")

    def save_data(self):
        """Saves specificity data to database."""
        print("🔵 save_data called!")
        
        if not self.project:
            print("🔴 No project!")
            QMessageBox.warning(self, "Error", "No project selected!")
            return
        
        # Get project ID
        if isinstance(self.project, (list, tuple)):
            project_id = self.project[0]
        else:
            project_id = self.project.id if hasattr(self.project, 'id') else None
        
        if not project_id:
            print("🔴 Invalid project ID!")
            QMessageBox.warning(self, "Error", "Invalid project!")
            return
        
        print(f"🟢 Project ID: {project_id}")
        
        # Helper function to safely convert to float
        def safe_float(value):
            if not value or value.strip() == "" or value.strip().upper() == "N/A":
                return 0.0
            try:
                return float(value)
            except ValueError:
                return 0.0
        
        # Collect data from rows
        rows_data = []
        for row in self.rows_data:
            rows_data.append({
                "name": row["name"].text(),
                "peak_detected": row["peak_detected"].currentText(),
                "rt": safe_float(row["rt"].text()),
                "area": safe_float(row["area"].text()),
                "rs": safe_float(row["rs"].text()),
                "interference": safe_float(row["interference"].text()),
                "status": row["status"].text()
            })
        
        print(f"🟢 Collected {len(rows_data)} rows")
        
        try:
            from database.database import save_specificity
            save_specificity(project_id, rows_data)
            print("✅ Data saved successfully!")
            QMessageBox.information(self, "Success", "Specificity data saved successfully!")
        except Exception as e:
            print(f"🔴 Error: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to save data:\n{str(e)}")