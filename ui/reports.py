"""
PharmaValidate v0.5 - Analytics Reports Tab
Displays complete validation reports with all module results
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QScrollArea, QTextBrowser, QMessageBox,
    QFileDialog, QSplitter, QGroupBox, QGridLayout, QTabWidget
)
from PySide6.QtCore import Qt

from database.database import (
    get_projects, get_project, get_protocol_by_project,
    get_specificity_results, get_linearity_results,
    get_accuracy_results, get_precision_results,
    get_robustness_ofat_results, get_robustness_doe_results,
    get_rel_sub_impurities, get_validation_summary,
    update_overall_status
)
from utils.report_pdf_generator import generate_validation_report_pdf


class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id = None
        self.build_ui()
        self.load_projects()

    def build_ui(self):
        self.setStyleSheet("background-color: #F8FAFC;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ============================================
        # HEADER: Project Selector
        # ============================================
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("📊 Validation Report")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        header_layout.addWidget(QLabel("Select Project:"))
        self.project_dropdown = QComboBox()
        self.project_dropdown.setFixedWidth(300)
        self.project_dropdown.setStyleSheet("padding: 6px; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.project_dropdown.currentIndexChanged.connect(self.on_project_selected)
        header_layout.addWidget(self.project_dropdown)

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setStyleSheet("padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.btn_refresh.clicked.connect(self.load_projects)
        header_layout.addWidget(self.btn_refresh)

        main_layout.addWidget(header_frame)

        # ============================================
        # MAIN CONTENT: Split View
        # ============================================
        splitter = QSplitter(Qt.Horizontal)

        # --- LEFT: Navigation / Summary ---
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Project Info
        self.project_info = QLabel("Select a project to view report")
        self.project_info.setWordWrap(True)
        self.project_info.setStyleSheet("font-size: 11px; color: #475569; padding: 5px; background-color: #F8FAFC; border-radius: 4px;")
        left_layout.addWidget(self.project_info)

        # Overall Status
        status_group = QGroupBox("Overall Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        status_layout = QVBoxLayout(status_group)
        
        self.lbl_overall_status = QLabel("PENDING")
        self.lbl_overall_status.setAlignment(Qt.AlignCenter)
        self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #94A3B8;")
        status_layout.addWidget(self.lbl_overall_status)
        
        self.lbl_status_text = QLabel("No data available")
        self.lbl_status_text.setAlignment(Qt.AlignCenter)
        self.lbl_status_text.setStyleSheet("font-size: 10px; color: #64748B;")
        status_layout.addWidget(self.lbl_status_text)
        
        left_layout.addWidget(status_group)

        # Module Status List
        modules_group = QGroupBox("Module Status")
        modules_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        modules_layout = QVBoxLayout(modules_group)
        
        self.module_status_labels = {
            "Specificity": QLabel("⏳ PENDING"),
            "Linearity": QLabel("⏳ PENDING"),
            "Accuracy": QLabel("⏳ PENDING"),
            "Precision": QLabel("⏳ PENDING"),
            "Robustness": QLabel("⏳ PENDING"),
            "Related Substances": QLabel("⏳ PENDING")
        }
        
        for name, label in self.module_status_labels.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{name}:"))
            row.addStretch()
            label.setStyleSheet("font-weight: bold; font-size: 11px;")
            row.addWidget(label)
            modules_layout.addLayout(row)
        
        left_layout.addWidget(modules_group)

        # Action Buttons
        self.btn_generate_pdf = QPushButton("📄 Generate PDF Report")
        self.btn_generate_pdf.setEnabled(False)
        self.btn_generate_pdf.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #172554; }
            QPushButton:disabled { background-color: #CBD5E1; color: #94A3B8; }
        """)
        self.btn_generate_pdf.clicked.connect(self.generate_pdf_report)
        left_layout.addWidget(self.btn_generate_pdf)

        self.btn_print = QPushButton("🖨️ Print Report")
        self.btn_print.setEnabled(False)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton:disabled { background-color: #CBD5E1; color: #94A3B8; }
        """)
        self.btn_print.clicked.connect(self.print_report)
        left_layout.addWidget(self.btn_print)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # --- RIGHT: Report Preview ---
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Report Tabs
        self.report_tabs = QTabWidget()
        self.report_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: white; }
            QTabBar::tab { padding: 8px 16px; font-weight: bold; }
            QTabBar::tab:selected { color: #1E3A8A; border-bottom: 2px solid #1E3A8A; }
        """)

        # Summary Tab
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_browser = QTextBrowser()
        self.summary_browser.setStyleSheet("border: none; background-color: #FFFFFF; padding: 10px;")
        summary_layout.addWidget(self.summary_browser)
        self.report_tabs.addTab(self.summary_tab, "Summary")

        # Module Tabs
        self.module_tabs = {}
        for module in ["Specificity", "Linearity", "Accuracy", "Precision", "Robustness", "Related Substances"]:
            tab = QWidget()
            layout = QVBoxLayout(tab)
            browser = QTextBrowser()
            browser.setStyleSheet("border: none; background-color: #FFFFFF; padding: 10px;")
            layout.addWidget(browser)
            self.module_tabs[module] = browser
            self.report_tabs.addTab(tab, module)

        right_layout.addWidget(self.report_tabs)
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)

        # ============================================
        # FOOTER
        # ============================================
        footer_frame = QFrame()
        footer_frame.setStyleSheet("border-top: 1px solid #E2E8F0;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 10, 10, 10)

        self.lbl_last_updated = QLabel("Select a project to begin")
        self.lbl_last_updated.setStyleSheet("color: #64748B; font-size: 10px;")
        footer_layout.addWidget(self.lbl_last_updated)

        footer_layout.addStretch()

        self.btn_export_excel = QPushButton("📊 Export to Excel")
        self.btn_export_excel.setEnabled(False)
        self.btn_export_excel.setStyleSheet("padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.btn_export_excel.clicked.connect(self.export_excel)
        footer_layout.addWidget(self.btn_export_excel)

        main_layout.addWidget(footer_frame)

    # ============================================
    # DATA LOADING
    # ============================================

    def load_projects(self):
        """Loads all projects into the dropdown."""
        self.project_dropdown.blockSignals(True)
        self.project_dropdown.clear()
        self.project_dropdown.addItem("--- Select a Project ---", None)

        projects = get_projects()
        print(f"🔵 Loaded {len(projects)} projects")  # Debug
        for proj in projects:
            p_id = proj[0]
            p_name = proj[1]
            protocol = proj[5] if len(proj) > 5 else ""
            self.project_dropdown.addItem(f"[{protocol}] {p_name}", p_id)

        self.project_dropdown.blockSignals(False)
        self.clear_report()

    def on_project_selected(self, index):
        """Handles project selection."""
        project_id = self.project_dropdown.currentData()
        print(f"🔵 Project selected: {project_id}")  # Debug
        if project_id is None:
            self.clear_report()
            return

        self.current_project_id = project_id
        self.load_report(project_id)

    # ============================================
    # REPORT GENERATION
    # ============================================

    def load_report(self, project_id):
        """Loads and displays the complete report for a project."""
        print(f"🔵 Loading report for project: {project_id}")  # Debug
        
        project = get_project(project_id)
        if not project:
            print("🔴 Project not found!")
            self.clear_report()
            return

        # FIXED: Safe unpacking captures the 8-item structure cleanly
        _, name, product, method, val_type, protocol, analyst, *_ = project

        self.project_info.setText(
            f"<b>Project:</b> {name}<br>"
            f"<b>Product:</b> {product}<br>"
            f"<b>Method:</b> {method}<br>"
            f"<b>Protocol:</b> {protocol}<br>"
            f"<b>Analyst:</b> {analyst}"
        )

        # Load all module data
        specificity_data = get_specificity_results(project_id)
        linearity_data = get_linearity_results(project_id)
        accuracy_data = get_accuracy_results(project_id)
        precision_data = get_precision_results(project_id)
        ofat_data = get_robustness_ofat_results(project_id)
        doe_data = get_robustness_doe_results(project_id)
        impurities = get_rel_sub_impurities(project_id)

        print(f"🟢 Specificity data: {len(specificity_data)} rows")  # Debug
        print(f"🟢 Linearity data: {len(linearity_data)} rows")  # Debug

        # Get protocol
        protocol_data = get_protocol_by_project(project_id)

        # Update summary status
        update_overall_status(project_id)
        summary = get_validation_summary(project_id)

        # Update module status labels
        self.update_status_labels(summary)

        # Update overall status
        if summary and summary.get("overall_status"):
            status = summary["overall_status"]
            self.lbl_overall_status.setText(status)
            if status == "PASS":
                self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #10B981;")
                self.lbl_status_text.setText("✅ All validation criteria met")
            elif status == "FAIL":
                self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #EF4444;")
                self.lbl_status_text.setText("❌ One or more modules failed")
            else:
                self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #F59E0B;")
                self.lbl_status_text.setText("⏳ Validation incomplete")
        else:
            self.lbl_overall_status.setText("PENDING")
            self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #94A3B8;")
            self.lbl_status_text.setText("No validation data available")

        # Generate report HTML
        self.generate_summary_html(project, protocol_data, summary)
        self.generate_specificity_html(specificity_data)
        self.generate_linearity_html(linearity_data)
        self.generate_accuracy_html(accuracy_data)
        self.generate_precision_html(precision_data)
        self.generate_robustness_html(ofat_data, doe_data)
        self.generate_rel_sub_html(impurities)

        # Enable buttons
        self.btn_generate_pdf.setEnabled(True)
        self.btn_print.setEnabled(True)
        self.btn_export_excel.setEnabled(True)

        self.lbl_last_updated.setText(f"Last updated: {summary.get('report_generated_date', 'N/A')}" if summary else "Data loaded")
        print("✅ Report loaded successfully!")  # Debug

    def clear_report(self):
        """Clears all report displays."""
        self.project_info.setText("Select a project to view report")
        self.lbl_overall_status.setText("PENDING")
        self.lbl_overall_status.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px; color: #94A3B8;")
        self.lbl_status_text.setText("No data available")

        for label in self.module_status_labels.values():
            label.setText("⏳ PENDING")
            label.setStyleSheet("font-weight: bold; font-size: 11px; color: #94A3B8;")

        self.summary_browser.clear()
        for browser in self.module_tabs.values():
            browser.clear()

        self.btn_generate_pdf.setEnabled(False)
        self.btn_print.setEnabled(False)
        self.btn_export_excel.setEnabled(False)

    def update_status_labels(self, summary):
        """Updates the module status labels."""
        print(f"🔵 Updating status labels with summary: {summary}")  # Debug
        
        status_map = {
            "specificity_status": ("Specificity", "PENDING"),
            "linearity_status": ("Linearity", "PENDING"),
            "accuracy_status": ("Accuracy", "PENDING"),
            "precision_status": ("Precision", "PENDING"),
            "robustness_status": ("Robustness", "PENDING"),
            "rel_sub_status": ("Related Substances", "PENDING")
        }

        if summary:
            print(f"🟢 Summary keys: {list(summary.keys())}")  # Debug

        for db_key, (label_name, default) in status_map.items():
            status = summary.get(db_key, default) if summary else default
            label = self.module_status_labels.get(label_name)

            if status == "PASS":
                label.setText("✅ PASS")
                label.setStyleSheet("font-weight: bold; font-size: 11px; color: #10B981;")
            elif status == "FAIL":
                label.setText("❌ FAIL")
                label.setStyleSheet("font-weight: bold; font-size: 11px; color: #EF4444;")
            else:
                label.setText("⏳ PENDING")
                label.setStyleSheet("font-weight: bold; font-size: 11px; color: #94A3B8;")

    # ============================================
    # HTML GENERATION METHODS
    # ============================================

    def generate_summary_html(self, project, protocol_data, summary):
        """Generates the summary tab HTML."""
        # FIXED: Safe unpacking parameters used here to match layout keys
        _, name, product, method, val_type, protocol, analyst, *_ = project

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #1E3A8A;">Validation Summary Report</h1>
            <hr style="border: 1px solid #E2E8F0;">
            
            <h2>Project Information</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 4px;"><b>Project Name:</b></td><td>{name}</td></tr>
                <tr><td style="padding: 4px;"><b>Product:</b></td><td>{product}</td></tr>
                <tr><td style="padding: 4px;"><b>Method:</b></td><td>{method}</td></tr>
                <tr><td style="padding: 4px;"><b>Validation Type:</b></td><td>{val_type}</td></tr>
                <tr><td style="padding: 4px;"><b>Protocol Number:</b></td><td>{protocol}</td></tr>
                <tr><td style="padding: 4px;"><b>Analyst:</b></td><td>{analyst}</td></tr>
            </table>
            
            <h2>Module Status Summary</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 8px; text-align: left;">Module</th>
                    <th style="padding: 8px; text-align: center;">Status</th>
                </tr>
        """

        statuses = [
            ("Specificity", summary.get("specificity_status", "PENDING") if summary else "PENDING"),
            ("Linearity", summary.get("linearity_status", "PENDING") if summary else "PENDING"),
            ("Accuracy", summary.get("accuracy_status", "PENDING") if summary else "PENDING"),
            ("Precision", summary.get("precision_status", "PENDING") if summary else "PENDING"),
            ("Robustness", summary.get("robustness_status", "PENDING") if summary else "PENDING"),
            ("Related Substances", summary.get("rel_sub_status", "PENDING") if summary else "PENDING")
        ]

        for name, status in statuses:
            color = "#10B981" if status == "PASS" else "#EF4444" if status == "FAIL" else "#94A3B8"
            html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #E2E8F0;">{name}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #E2E8F0; text-align: center; color: {color}; font-weight: bold;">{status}</td>
                </tr>
            """

        overall = summary.get("overall_status", "PENDING") if summary else "PENDING"
        overall_color = "#10B981" if overall == "PASS" else "#EF4444" if overall == "FAIL" else "#94A3B8"

        html += f"""
                <tr style="background-color: #F8FAFC;">
                    <td style="padding: 8px; font-weight: bold;">OVERALL STATUS</td>
                    <td style="padding: 8px; text-align: center; color: {overall_color}; font-weight: bold; font-size: 16px;">{overall}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px; color: #64748B; font-size: 12px;">
                <i>Report generated: {summary.get('report_generated_date', 'N/A') if summary else 'N/A'}</i>
            </p>
        </div>
        """

        self.summary_browser.setHtml(html)

    def generate_specificity_html(self, data):
        """Generates the Specificity tab HTML."""
        if not data:
            html = """
            <div style="padding: 20px; color: #64748B; text-align: center;">
                <p>No Specificity data available for this project.</p>
                <p style="font-size: 11px;">Please save data from the Specificity module first.</p>
            </div>
            """
            self.module_tabs["Specificity"].setHtml(html)
            return

        html = """
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Specificity Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: left;">Sample Type</th>
                    <th style="padding: 6px; text-align: center;">Peak</th>
                    <th style="padding: 6px; text-align: center;">Rt (min)</th>
                    <th style="padding: 6px; text-align: center;">Area</th>
                    <th style="padding: 6px; text-align: center;">Resolution</th>
                    <th style="padding: 6px; text-align: center;">Interference (%)</th>
                    <th style="padding: 6px; text-align: center;">Status</th>
                </tr>
        """

        for row in data:
            sample_type, peak_detected, rt, area, res, interference, status = row
            color = "#10B981" if status == "PASS" else "#EF4444" if status == "FAIL" else "#94A3B8"
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0;">{sample_type}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{peak_detected}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{rt if rt else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{area if area else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{res if res else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{interference}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center; color: {color}; font-weight: bold;">{status}</td>
                </tr>
            """

        html += "</table></div>"
        self.module_tabs["Specificity"].setHtml(html)

    def generate_linearity_html(self, data):
        """Generates the Linearity tab HTML."""
        if not data:
            html = """
            <div style="padding: 20px; color: #64748B; text-align: center;">
                <p>No Linearity data available for this project.</p>
                <p style="font-size: 11px;">Please save data from the Linearity module first.</p>
            </div>
            """
            self.module_tabs["Linearity"].setHtml(html)
            return

        first_row = data[0]
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Linearity Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
            
            <h3>Summary Statistics</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
        """

        summary_fields = [
            ("Slope", first_row[10]),
            ("Intercept", first_row[11]),
            ("R²", first_row[12]),
            ("% Y-Intercept", first_row[13]),
            ("Pooled % RSD", first_row[17] if len(first_row) > 17 else "N/A"),
            ("Overall Status", first_row[20] if len(first_row) > 20 else "PENDING")
        ]

        for label, value in summary_fields:
            color = "#10B981" if value == "PASS" else "#EF4444" if value == "FAIL" else "#1E3A8A"
            html += f"""
                <tr>
                    <td style="padding: 4px; font-weight: bold;">{label}:</td>
                    <td style="padding: 4px; color: {color};">{value}</td>
                </tr>
            """

        html += """
            </table>
            
            <h3>Level Data</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: center;">Level</th>
                    <th style="padding: 6px; text-align: center;">Nom (%)</th>
                    <th style="padding: 6px; text-align: center;">W1</th>
                    <th style="padding: 6px; text-align: center;">W2</th>
                    <th style="padding: 6px; text-align: center;">W3</th>
                    <th style="padding: 6px; text-align: center;">A1</th>
                    <th style="padding: 6px; text-align: center;">A2</th>
                    <th style="padding: 6px; text-align: center;">A3</th>
                    <th style="padding: 6px; text-align: center;">Mean</th>
                    <th style="padding: 6px; text-align: center;">% RSD</th>
                </tr>
        """

        for row in data:
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[1]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[2]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[3]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[4]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[5]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[6]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[7]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[8]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[9]}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[10]}</td>
                </tr>
            """

        html += "</table></div>"
        self.module_tabs["Linearity"].setHtml(html)

    def generate_accuracy_html(self, data):
        """Generates the Accuracy tab HTML."""
        if not data:
            html = """
            <div style="padding: 20px; color: #64748B; text-align: center;">
                <p>No Accuracy data available for this project.</p>
                <p style="font-size: 11px;">Please save data from the Accuracy module first.</p>
            </div>
            """
            self.module_tabs["Accuracy"].setHtml(html)
            return

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Accuracy Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
            
            <h3>SST Results</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr>
                    <td style="padding: 4px; font-weight: bold;">SST Mean:</td>
                    <td style="padding: 4px;">{data[6] if len(data) > 6 else "N/A"}</td>
                    <td style="padding: 4px; font-weight: bold;">SST % RSD:</td>
                    <td style="padding: 4px;">{data[7] if len(data) > 7 else "N/A"}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; font-weight: bold;">Matrix Response:</td>
                    <td style="padding: 4px;">{data[8] if len(data) > 8 else "N/A"}</td>
                    <td style="padding: 4px; font-weight: bold;">Std Weight:</td>
                    <td style="padding: 4px;">{data[9] if len(data) > 9 else "N/A"}</td>
                </tr>
            </table>

            <h3>Recovery Levels</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: center;">Level</th>
                    <th style="padding: 6px; text-align: center;">Mean Recovery (%)</th>
                    <th style="padding: 6px; text-align: center;">% RSD</th>
                    <th style="padding: 6px; text-align: center;">Bias (%)</th>
                    <th style="padding: 6px; text-align: center;">Status</th>
                </tr>
        """

        # Level 80
        if len(data) > 24:
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">80%</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[21] if len(data) > 21 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[22] if len(data) > 22 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[23] if len(data) > 23 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center; color: { '#10B981' if data[24] == 'PASS' else '#EF4444' };">{data[24] if len(data) > 24 else "N/A"}</td>
                </tr>
            """

        # Level 100
        if len(data) > 39:
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">100%</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[36] if len(data) > 36 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[37] if len(data) > 37 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[38] if len(data) > 38 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center; color: { '#10B981' if data[39] == 'PASS' else '#EF4444' };">{data[39] if len(data) > 39 else "N/A"}</td>
                </tr>
            """

        # Level 120
        if len(data) > 54:
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">120%</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[51] if len(data) > 51 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[52] if len(data) > 52 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{data[53] if len(data) > 53 else "N/A"}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center; color: { '#10B981' if data[54] == 'PASS' else '#EF4444' };">{data[54] if len(data) > 54 else "N/A"}</td>
                </tr>
            """

        html += """
            </table>
            
            <h3>Overall Summary</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
        """

        if len(data) > 59:
            html += f"""
                <tr><td style="padding: 4px; font-weight: bold;">Overall Mean Recovery:</td><td>{data[55] if len(data) > 55 else "N/A"}%</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Overall % RSD:</td><td>{data[56] if len(data) > 56 else "N/A"}%</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Overall Bias:</td><td>{data[57] if len(data) > 57 else "N/A"}%</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Pooled SD:</td><td>{data[58] if len(data) > 58 else "N/A"}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Overall Status:</td>
                    <td style="color: { '#10B981' if data[59] == 'PASS' else '#EF4444' };">{data[59] if len(data) > 59 else "N/A"}</td></tr>
            """

        html += "</table></div>"
        self.module_tabs["Accuracy"].setHtml(html)

    def generate_precision_html(self, data):
        """Generates the Precision tab HTML."""
        if not data:
            html = """
            <div style="padding: 20px; color: #64748B; text-align: center;">
                <p>No Precision data available for this project.</p>
                <p style="font-size: 11px;">Please save data from the Precision module first.</p>
            </div>
            """
            self.module_tabs["Precision"].setHtml(html)
            return

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Precision Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
            
            <h3>Repeatability (Analyst 1 / Day 1)</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr><td style="padding: 4px; font-weight: bold;">Replicates:</td>
                    <td>{data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}, {data[6]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Mean:</td><td>{data[7]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">SD:</td><td>{data[8]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">% RSD:</td><td>{data[9]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Status:</td>
                    <td style="color: { '#10B981' if data[10] == 'PASS' else '#EF4444' };">{data[10]}</td></tr>
            </table>

            <h3>Intermediate Precision (Analyst 2 / Day 2)</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr><td style="padding: 4px; font-weight: bold;">Replicates:</td>
                    <td>{data[11]}, {data[12]}, {data[13]}, {data[14]}, {data[15]}, {data[16]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Mean:</td><td>{data[17]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">SD:</td><td>{data[18]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">% RSD:</td><td>{data[19]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Status:</td>
                    <td style="color: { '#10B981' if data[20] == 'PASS' else '#EF4444' };">{data[20]}</td></tr>
            </table>

            <h3>Combined Precision</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr><td style="padding: 4px; font-weight: bold;">Combined Mean (N=12):</td><td>{data[21]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Pooled SD:</td><td>{data[22]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Combined % RSD:</td><td>{data[23]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Overall Status:</td>
                    <td style="color: { '#10B981' if data[24] == 'PASS' else '#EF4444' };">{data[24]}</td></tr>
            </table>
        </div>
        """
        self.module_tabs["Precision"].setHtml(html)

    def generate_robustness_html(self, ofat_data, doe_data):
        """Generates the Robustness tab HTML."""
        html = """
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Robustness Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
        """

        if ofat_data:
            html += """
            <h3>OFAT Robustness</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: left;">Parameter</th>
                    <th style="padding: 6px; text-align: center;">Rt</th>
                    <th style="padding: 6px; text-align: center;">Tailing</th>
                    <th style="padding: 6px; text-align: center;">Plates</th>
                    <th style="padding: 6px; text-align: center;">Assay (%)</th>
                    <th style="padding: 6px; text-align: center;">Dev (%)</th>
                    <th style="padding: 6px; text-align: center;">Status</th>
                </tr>
            """

            for row in ofat_data:
                color = "#10B981" if row[9] == "PASS" else "#EF4444" if row[9] == "FAIL" else "#94A3B8"
                nominal_marker = "⭐ " if row[8] else ""
                html += f"""
                    <tr>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0;">{nominal_marker}{row[2]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[3]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[4]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[5]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[6]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{row[7]}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center; color: {color}; font-weight: bold;">{row[9]}</td>
                    </tr>
                """
            html += "</table>"

        if doe_data:
            html += """
            <h3>DOE (2³ Full Factorial) Results</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
            """

            html += f"""
                <tr><td style="padding: 4px; font-weight: bold;">Factor A:</td><td>{doe_data[2]} (Low: {doe_data[5]}, High: {doe_data[6]})</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Factor B:</td><td>{doe_data[3]} (Low: {doe_data[7]}, High: {doe_data[8]})</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Factor C:</td><td>{doe_data[4]} (Low: {doe_data[9]}, High: {doe_data[10]})</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Effect A:</td><td>{doe_data[19]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Effect B:</td><td>{doe_data[20]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Effect C:</td><td>{doe_data[21]}</td></tr>
                <tr><td style="padding: 4px; font-weight: bold;">Dominant Factor:</td><td style="color: #1E3A8A; font-weight: bold;">{doe_data[22]}</td></tr>
            </table>

            <h3>DOE Run Data</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: center;">Run</th>
                    <th style="padding: 6px; text-align: center;">A</th>
                    <th style="padding: 6px; text-align: center;">B</th>
                    <th style="padding: 6px; text-align: center;">C</th>
                    <th style="padding: 6px; text-align: center;">Response</th>
                </tr>
            """

            run_levels = [
                ("-", "-", "-"), ("+", "-", "-"), ("-", "+", "-"), ("+", "+", "-"),
                ("-", "-", "+"), ("+", "-", "+"), ("-", "+", "+"), ("+", "+", "+")
            ]

            for i, (a, b, c) in enumerate(run_levels):
                response = doe_data[11 + i] if len(doe_data) > 11 + i else "N/A"
                html += f"""
                    <tr>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{i+1}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{a}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{b}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{c}</td>
                        <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{response}</td>
                    </tr>
                """

            html += "</table>"

        if not ofat_data and not doe_data:
            html += """
            <p style="color: #64748B; text-align: center;">No Robustness data available for this project.</p>
            """

        html += "</div>"
        self.module_tabs["Robustness"].setHtml(html)

    def generate_rel_sub_html(self, impurities):
        """Generates the Related Substances tab HTML."""
        if not impurities:
            html = """
            <div style="padding: 20px; color: #64748B; text-align: center;">
                <p>No Related Substances data available for this project.</p>
                <p style="font-size: 11px;">Please save data from the Related Substances module first.</p>
            </div>
            """
            self.module_tabs["Related Substances"].setHtml(html)
            return

        html = """
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1E3A8A;">Related Substances Results</h2>
            <hr style="border: 1px solid #E2E8F0;">
            
            <h3>Impurity Registry</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 6px; text-align: left;">Impurity</th>
                    <th style="padding: 6px; text-align: center;">Spec Limit (%)</th>
                    <th style="padding: 6px; text-align: center;">Use RRF</th>
                    <th style="padding: 6px; text-align: center;">RRF Value</th>
                </tr>
        """

        for imp in impurities:
            imp_id, name, spec_limit, use_rrf, rrf_value = imp
            html += f"""
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0;">{name}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{spec_limit}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{'Yes' if use_rrf else 'No'}</td>
                    <td style="padding: 6px; border-bottom: 1px solid #E2E8F0; text-align: center;">{rrf_value}</td>
                </tr>
            """

        html += """
            </table>
            
            <p style="margin-top: 20px; color: #64748B; font-size: 12px;">
                <i>Note: Full Related Substances validation includes LOD/LOQ, Linearity, and Accuracy for each impurity.
                Please refer to individual module data for detailed results.</i>
            </p>
        </div>
        """
        self.module_tabs["Related Substances"].setHtml(html)

    # ============================================
    # PDF GENERATION
    # ============================================

    def generate_pdf_report(self):
        """Generates and saves a PDF report."""
        if not self.current_project_id:
            QMessageBox.warning(self, "Error", "No project selected!")
            return

        project = get_project(self.current_project_id)
        if not project:
            QMessageBox.warning(self, "Error", "Project not found!")
            return

        # Get all data
        data = {
            "project": project,
            "protocol": get_protocol_by_project(self.current_project_id),
            "specificity": get_specificity_results(self.current_project_id),
            "linearity": get_linearity_results(self.current_project_id),
            "accuracy": get_accuracy_results(self.current_project_id),
            "precision": get_precision_results(self.current_project_id),
            "ofat": get_robustness_ofat_results(self.current_project_id),
            "doe": get_robustness_doe_results(self.current_project_id),
            "impurities": get_rel_sub_impurities(self.current_project_id),
            "summary": get_validation_summary(self.current_project_id)
        }

        # Save dialog
        project_name = project[1]
        default_filename = f"{project_name}_Validation_Report.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", default_filename, "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                generate_validation_report_pdf(file_path, data)
                QMessageBox.information(self, "Success", f"PDF Report saved to:\n{file_path}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{str(e)}")

    def print_report(self):
        """Prints the current report."""
        QMessageBox.information(self, "Print", "Print functionality will be implemented in the next version.\nPlease use the PDF export and print from your PDF viewer.")

    def export_excel(self):
        """Exports report to Excel."""
        QMessageBox.information(self, "Excel Export", "Excel export will be implemented in the next version.")