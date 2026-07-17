"""
PharmaValidate v0.5 - Wizard Protocol Creator
Features a dynamic split-pane UI supporting Assay, Dissolution, and Related Substances (RS) testing.
Includes customizable calculations, LOD/LOQ tracking, and dynamic math layouts.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextBrowser,
    QPushButton, QMessageBox, QFrame, QFileDialog, QLineEdit, QCheckBox,
    QScrollArea, QButtonGroup, QRadioButton, QTabWidget, QPlainTextEdit,
    QGroupBox, QGridLayout
)

from database.database import get_projects, get_project
from utils.pdf_generator import generate_assay_pdf


class ProtocolPage(QWidget):

    def __init__(self):
        super().__init__()
        self.active_project_data = None
        self.checkbox_map = {}
        self.build_ui()

    def build_ui(self):
        self.setStyleSheet("background-color: #F8FAFC;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # -------------------------------------------------------------
        # Header Selector Card
        # -------------------------------------------------------------
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(15, 10, 15, 10)

        title_layout = QVBoxLayout()
        title = QLabel("📑 Universal Protocol Workspace")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0F172A;")
        subtitle = QLabel("Design validation / verification study designs for Assay, Dissolution, or Related Substances.")
        subtitle.setStyleSheet("font-size: 11px; color: #64748B;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        h_layout.addLayout(title_layout)

        h_layout.addStretch()

        self.project_dropdown = QComboBox()
        self.project_dropdown.setFixedWidth(280)
        self.project_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px;
                color: #0F172A;
            }
        """)
        self.project_dropdown.currentIndexChanged.connect(self.on_project_selected)
        h_layout.addWidget(self.project_dropdown)

        main_layout.addWidget(header_card)

        # -------------------------------------------------------------
        # Split Workspace Layout
        # -------------------------------------------------------------
        body_layout = QHBoxLayout()
        body_layout.setSpacing(15)

        # --- LEFT PANEL: MULTI-TAB SURVEY WIZARD ---
        self.survey_panel = QFrame()
        self.survey_panel.setFixedWidth(380)
        self.survey_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        survey_layout = QVBoxLayout(self.survey_panel)
        survey_layout.setContentsMargins(10, 10, 10, 10)

        self.survey_tabs = QTabWidget()
        self.survey_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; border-radius: 4px; background: white; }
            QTabBar::tab { font-size: 11px; font-weight: bold; padding: 8px 12px; color: #475569; }
            QTabBar::tab:selected { color: #1E3A8A; background: #FFFFFF; }
        """)

        # -------------------------------------------------------------
        # TAB 1: STUDY SCOPE
        # -------------------------------------------------------------
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.setSpacing(10)

        comp_label = QLabel("Company Name:")
        comp_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_company = QLineEdit("Pharma Labs Inc.")
        self.txt_company.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px; color:#334155;")
        self.txt_company.textChanged.connect(self.update_live_preview)
        tab1_layout.addWidget(comp_label)
        tab1_layout.addWidget(self.txt_company)

        # Test Category Dropdown
        test_lbl = QLabel("Test Category:")
        test_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.cmb_test_type = QComboBox()
        self.cmb_test_type.addItems(["Assay", "Dissolution", "Related Substances (RS)"])
        self.cmb_test_type.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px; color:#334155;")
        self.cmb_test_type.currentIndexChanged.connect(self.on_test_type_changed)
        tab1_layout.addWidget(test_lbl)
        tab1_layout.addWidget(self.cmb_test_type)

        study_label = QLabel("Study Methodology Type:")
        study_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        tab1_layout.addWidget(study_label)

        self.toggle_group = QButtonGroup(self)
        radio_layout = QHBoxLayout()
        self.rad_validation = QRadioButton("Method Validation")
        self.rad_validation.setChecked(True)
        self.rad_verification = QRadioButton("Method Verification")
        self.toggle_group.addButton(self.rad_validation)
        self.toggle_group.addButton(self.rad_verification)
        self.toggle_group.buttonClicked.connect(self.on_study_type_changed)
        radio_layout.addWidget(self.rad_validation)
        radio_layout.addWidget(self.rad_verification)
        tab1_layout.addLayout(radio_layout)

        param_label = QLabel("Select Target Study Parameters:")
        param_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        tab1_layout.addWidget(param_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #FFFFFF;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)

        # Re-introducing LOD and LOQ to the list of selectable parameter targets
        all_params = [
            "System Suitability", "Specificity", "LOD", "LOQ", 
            "Linearity & Range", "Accuracy (Recovery)", 
            "Precision (Repeatability)", "Intermediate Precision", "Robustness"
        ]
        for param in all_params:
            chk = QCheckBox(param)
            chk.setStyleSheet("QCheckBox { font-size: 11px; color: #334155; }")
            chk.stateChanged.connect(self.update_live_preview)
            scroll_layout.addWidget(chk)
            self.checkbox_map[param] = chk

        scroll_area.setWidget(scroll_widget)
        tab1_layout.addWidget(scroll_area)
        self.survey_tabs.addTab(tab1_widget, "Scope")

        # -------------------------------------------------------------
        # TAB 2: METHODOLOGY & HPLC
        # -------------------------------------------------------------
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)
        tab2_layout.setSpacing(10)

        # Reference Standard Preparation Input
        std_label = QLabel("Reference Standard Prep:")
        std_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_std_prep = QPlainTextEdit()
        self.txt_std_prep.setPlaceholderText("Weigh reference standard into a flask, dissolve with diluent...")
        self.txt_std_prep.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; color: #334155;")
        self.txt_std_prep.textChanged.connect(self.update_live_preview)
        tab2_layout.addWidget(std_label)
        tab2_layout.addWidget(self.txt_std_prep, 1)

        # Sample Preparation Input
        sample_label = QLabel("Sample Preparation Strategy:")
        sample_label.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_sample_prep = QPlainTextEdit()
        self.txt_sample_prep.setPlaceholderText("Prepare physical sample dilution matrices here...")
        self.txt_sample_prep.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; color: #334155;")
        self.txt_sample_prep.textChanged.connect(self.update_live_preview)
        tab2_layout.addWidget(sample_label)
        tab2_layout.addWidget(self.txt_sample_prep, 1)

        # HPLC conditions toggle & setup
        self.chk_is_hplc = QCheckBox("Apply Chromatographic Conditions (HPLC)")
        self.chk_is_hplc.setStyleSheet("font-weight: bold; font-size: 11px; color: #1E3A8A;")
        self.chk_is_hplc.stateChanged.connect(self.toggle_hplc_layout)
        tab2_layout.addWidget(self.chk_is_hplc)

        self.hplc_group = QGroupBox("HPLC Operating Setup")
        self.hplc_group.setStyleSheet("QGroupBox { font-size: 10px; font-weight: bold; color: #475569; }")
        hplc_layout = QGridLayout(self.hplc_group)
        hplc_layout.setSpacing(6)

        hplc_layout.addWidget(QLabel("Column:"), 0, 0)
        self.txt_column = QLineEdit("C18, 250mm x 4.6mm, 5µm")
        hplc_layout.addWidget(self.txt_column, 0, 1)

        hplc_layout.addWidget(QLabel("Flow (mL/min):"), 1, 0)
        self.txt_flow = QLineEdit("1.0 mL/min")
        hplc_layout.addWidget(self.txt_flow, 1, 1)

        hplc_layout.addWidget(QLabel("Temp (°C):"), 2, 0)
        self.txt_temp = QLineEdit("30 °C")
        hplc_layout.addWidget(self.txt_temp, 2, 1)

        hplc_layout.addWidget(QLabel("Wavelength:"), 3, 0)
        self.txt_wavelength = QLineEdit("228 nm")
        hplc_layout.addWidget(self.txt_wavelength, 3, 1)

        hplc_layout.addWidget(QLabel("Injection Vol:"), 4, 0)
        self.txt_inj_vol = QLineEdit("20 µL")
        hplc_layout.addWidget(self.txt_inj_vol, 4, 1)

        hplc_layout.addWidget(QLabel("Mobile Phase:"), 5, 0)
        self.txt_mobile = QLineEdit("Buffer : Methanol (75:25)")
        hplc_layout.addWidget(self.txt_mobile, 5, 1)

        for fld in [self.txt_column, self.txt_flow, self.txt_temp, self.txt_wavelength, self.txt_inj_vol, self.txt_mobile]:
            fld.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 2px; color:#334155; font-size: 11px;")
            fld.textChanged.connect(self.update_live_preview)

        tab2_layout.addWidget(self.hplc_group)
        self.hplc_group.setVisible(False)

        # --- Dynamic Robustness Experimental Design Settings ---
        self.robustness_group = QGroupBox("Robustness Evaluation Strategy")
        self.robustness_group.setStyleSheet("QGroupBox { font-size: 10px; font-weight: bold; color: #475569; }")
        robustness_layout = QVBoxLayout(self.robustness_group)
        robustness_layout.setSpacing(6)

        robustness_lbl = QLabel("Robustness Approach Model:")
        robustness_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.cmb_robustness_type = QComboBox()
        self.cmb_robustness_type.addItems([
            "One Factor at a Time (OFAT)",
            "Full Factorial Design",
            "Both (OFAT & Full Factorial)"
        ])
        self.cmb_robustness_type.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px; color:#334155; font-size: 11px;")
        self.cmb_robustness_type.currentIndexChanged.connect(self.update_live_preview)

        robustness_layout.addWidget(robustness_lbl)
        robustness_layout.addWidget(self.cmb_robustness_type)
        
        # Additional robustness parameters
        self.chk_robustness_variables = QCheckBox("Include detailed robustness parameters table")
        self.chk_robustness_variables.setChecked(True)
        self.chk_robustness_variables.setStyleSheet("font-size: 10px; color: #475569;")
        self.chk_robustness_variables.stateChanged.connect(self.update_live_preview)
        robustness_layout.addWidget(self.chk_robustness_variables)
        
        tab2_layout.addWidget(self.robustness_group)
        self.robustness_group.setVisible(False)  # Hidden by default, toggled via parameters

        self.survey_tabs.addTab(tab2_widget, "Methodology")

        # -------------------------------------------------------------
        # TAB 3: CALCULATION FORMULA & MATH (NEW!)
        # -------------------------------------------------------------
        tab3_widget = QWidget()
        tab3_layout = QVBoxLayout(tab3_widget)
        tab3_layout.setSpacing(10)

        form_lbl = QLabel("Custom Mathematical Model Formula:")
        form_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_formula = QPlainTextEdit()
        self.txt_formula.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; color: #1E293B; font-family: monospace;")
        self.txt_formula.textChanged.connect(self.update_live_preview)
        tab3_layout.addWidget(form_lbl)
        tab3_layout.addWidget(self.txt_formula, 1)

        def_lbl = QLabel("Variable Definitions:")
        def_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_formula_defs = QPlainTextEdit()
        self.txt_formula_defs.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; color: #334155; font-size: 11px;")
        self.txt_formula_defs.textChanged.connect(self.update_live_preview)
        tab3_layout.addWidget(def_lbl)
        tab3_layout.addWidget(self.txt_formula_defs, 2)

        self.survey_tabs.addTab(tab3_widget, "Formula")

        # -------------------------------------------------------------
        # TAB 4: SYSTEM ACCEPTANCE LIMITS
        # -------------------------------------------------------------
        tab4_widget = QWidget()
        tab4_layout = QVBoxLayout(tab4_widget)
        tab4_layout.setSpacing(12)

        tab4_layout.addWidget(QLabel("<b>Acceptance Specifications</b>"))

        rsd_lbl = QLabel("Max Area Relative Standard Deviation (RSD):")
        rsd_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_limit_rsd = QLineEdit("2.0%")
        tab4_layout.addWidget(rsd_lbl)
        tab4_layout.addWidget(self.txt_limit_rsd)

        tail_lbl = QLabel("Maximum Peak Tailing Factor Limit:")
        tail_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_limit_tailing = QLineEdit("2.0")
        tab4_layout.addWidget(tail_lbl)
        tab4_layout.addWidget(self.txt_limit_tailing)

        rec_lbl = QLabel("Accuracy Recovery Target Range Limit:")
        rec_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 11px;")
        self.txt_limit_recovery = QLineEdit("98.0% - 102.0%")
        tab4_layout.addWidget(rec_lbl)
        tab4_layout.addWidget(self.txt_limit_recovery)

        for limit_fld in [self.txt_limit_rsd, self.txt_limit_tailing, self.txt_limit_recovery]:
            limit_fld.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px; color:#334155;")
            limit_fld.textChanged.connect(self.update_live_preview)

        tab4_layout.addStretch()
        self.survey_tabs.addTab(tab4_widget, "Limits")

        # Pack nested tab system to survey column
        survey_layout.addWidget(self.survey_tabs)
        body_layout.addWidget(self.survey_panel)

        # --- RIGHT PANEL: LIVE DOCUMENT VIEW ---
        self.preview_panel = QFrame()
        self.preview_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        preview_layout = QVBoxLayout(self.preview_panel)
        preview_layout.setContentsMargins(15, 15, 15, 15)

        self.preview_browser = QTextBrowser()
        self.preview_browser.setStyleSheet("border: none; background-color: #FFFFFF;")
        preview_layout.addWidget(self.preview_browser)

        body_layout.addWidget(self.preview_panel, 1)
        main_layout.addLayout(body_layout)

        # -------------------------------------------------------------
        # Footer Action Strip
        # -------------------------------------------------------------
        footer_layout = QHBoxLayout()
        
        self.btn_refresh = QPushButton("🔄 Reload")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; color: #475569; font-weight: bold;
                padding: 10px 15px; border-radius: 6px; border: 1px solid #CBD5E1;
            }
            QPushButton:hover { background-color: #F1F5F9; }
        """)
        self.btn_refresh.clicked.connect(self.load_active_projects)
        footer_layout.addWidget(self.btn_refresh)

        footer_layout.addStretch()

        self.btn_generate = QPushButton("📄 Compile PDF Report")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A; color: white; font-weight: bold;
                padding: 12px 24px; border-radius: 6px; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #172554; }
            QPushButton:disabled { background-color: #CBD5E1; color: #94A3B8; }
        """)
        self.btn_generate.clicked.connect(self.export_protocol_pdf)
        self.btn_generate.setEnabled(False)
        footer_layout.addWidget(self.btn_generate)

        main_layout.addLayout(footer_layout)
        
        self.survey_panel.setEnabled(False)
        self.load_active_projects()

    # -----------------------------------------------------------------
    # Interaction & Regulatory Guidance Logic
    # -----------------------------------------------------------------
    def load_active_projects(self):
        self.project_dropdown.blockSignals(True)
        self.project_dropdown.clear()
        self.project_dropdown.addItem("--- Select an Active Project ---", None)
        
        for proj in get_projects():
            p_id, p_name, _, _, _, p_protocol, _ = proj
            self.project_dropdown.addItem(f"[{p_protocol}] {p_name}", p_id)
            
        self.project_dropdown.blockSignals(False)
        self.preview_browser.setHtml(
            "<h3 style='color:#64748B; text-align:center; margin-top:100px;'>"
            "Select an active validation project from the dropdown to initialize workspace...</h3>"
        )
        self.survey_panel.setEnabled(False)
        self.btn_generate.setEnabled(False)

    def on_project_selected(self):
        project_id = self.project_dropdown.currentData()
        if project_id is None:
            self.survey_panel.setEnabled(False)
            self.btn_generate.setEnabled(False)
            self.preview_browser.clear()
            return

        self.active_project_data = get_project(project_id)
        if self.active_project_data:
            _, name, product, method, val_type, protocol, analyst = self.active_project_data
            self.survey_panel.setEnabled(True)
            self.btn_generate.setEnabled(True)
            
            if "hplc" in method.lower():
                self.chk_is_hplc.setChecked(True)
                self.hplc_group.setVisible(True)
            else:
                self.chk_is_hplc.setChecked(False)
                self.hplc_group.setVisible(False)

            self.apply_regulatory_defaults()

    def on_study_type_changed(self):
        self.apply_regulatory_defaults()

    def on_test_type_changed(self):
        self.apply_regulatory_defaults()

    def apply_regulatory_defaults(self):
        """Applies dynamic mathematical models, limit ranges, and checkboxes using ICH Guidelines."""
        if not self.active_project_data:
            return

        test_type = self.cmb_test_type.currentText()
        is_validation = self.rad_validation.isChecked()

        # 1. Parameter checklist dynamic toggling
        for chk in self.checkbox_map.values():
            chk.blockSignals(True)
            chk.setChecked(False)

        if test_type == "Assay":
            defaults = ["System Suitability", "Specificity", "Linearity & Range", "Accuracy (Recovery)", "Precision (Repeatability)", "Robustness"]
            # Auto-populate mathematical assay equations and definitions
            self.txt_formula.setPlainText("Assay (%) = [ (At * WStd * P * Avg.wt * 100) / (As * Wt * LC * 100) ]")
            self.txt_formula_defs.setPlainText(
                "Where:\n"
                "At = Peak response area of target sample preparation\n"
                "As = Mean peak area of working reference standard injection\n"
                "WStd = Weight of reference standard used (mg)\n"
                "Wt = Weight of physical sample used (mg)\n"
                "Avg.wt = Average tablet weight specification (mg)\n"
                "P = Certified purity/potency of standard (%)\n"
                "LC = Label claim of active ingredient (mg)"
            )
            # Standard Assay Limits
            self.txt_limit_rsd.setText("2.0%")
            self.txt_limit_recovery.setText("98.0% - 102.0%")

        elif test_type == "Dissolution":
            defaults = ["System Suitability", "Specificity", "Linearity & Range", "Accuracy (Recovery)", "Precision (Repeatability)", "Robustness"]
            # Auto-populate Dissolution Volume and dilution math models
            self.txt_formula.setPlainText("Dissolution (%) = [ (At * WStd * P * 900 * C_dil * 100) / (As * LC * 100) ]")
            self.txt_formula_defs.setPlainText(
                "Where:\n"
                "At = Chromatographic response area of dissolution aliquot\n"
                "As = Mean peak area of working reference standard injection\n"
                "WStd = Weight of standard component (mg)\n"
                "900 = Volume of specified vessel dissolution medium (mL)\n"
                "C_dil = Standard concentration dilution factor\n"
                "P = Certified standard potency (%)\n"
                "LC = Label claim of tablet active dosage (mg)"
            )
            # Dissolution Limits
            self.txt_limit_rsd.setText("2.0%")
            self.txt_limit_recovery.setText("Q - 20% to Q + 20%")

        elif test_type == "Related Substances (RS)":
            # LOD/LOQ restored as default parameters for impurity methods
            defaults = ["System Suitability", "Specificity", "LOD", "LOQ", "Linearity & Range", "Accuracy (Recovery)", "Precision (Repeatability)", "Intermediate Precision", "Robustness"]
            # Auto-populate Relative Response Factor (RRF) impurity math
            self.txt_formula.setPlainText("Individual Impurity (%) = [ (Ai * WStd * P * D_sample * 100) / (As_diluted * Wt * RRF * 100) ]")
            self.txt_formula_defs.setPlainText(
                "Where:\n"
                "Ai = Peak area of individual identified impurity component\n"
                "As_diluted = Peak area of main drug active in diluted standard preparation\n"
                "WStd = Weight of working standard (mg)\n"
                "Wt = Weight of raw sample matrix (mg)\n"
                "RRF = Relative Response Factor of specific target impurity\n"
                "D_sample = Relative dilution ratio matrix multiplier"
            )
            # RS Limits
            self.txt_limit_rsd.setText("10.0%")
            self.txt_limit_recovery.setText("80.0% - 120.0%")

        # Verification overrides (Simplified checklist protocol targets)
        if not is_validation:
            defaults = ["System Suitability", "Specificity", "Precision (Repeatability)"]

        for param in defaults:
            if param in self.checkbox_map:
                self.checkbox_map[param].setChecked(True)

        for chk in self.checkbox_map.values():
            chk.blockSignals(False)
            
        self.update_live_preview()

    def toggle_hplc_layout(self, state):
        self.hplc_group.setVisible(state == Qt.Checked)
        self.update_live_preview()

    def get_selected_parameters(self):
        return [param for param, chk in self.checkbox_map.items() if chk.isChecked()]

    def update_live_preview(self):
        """Compiles standard html formatting into the live preview browser."""
        if not self.active_project_data:
            return

        _, name, product, method, val_type, protocol, analyst = self.active_project_data
        company = self.txt_company.text() if self.txt_company.text() else "Analytical Laboratory"
        study_type = "Validation" if self.rad_validation.isChecked() else "Verification"
        test_type = self.cmb_test_type.currentText()
        selected_params = self.get_selected_parameters()

        # Handle visibility logic for the new Robustness configuration group in Tab 2
        is_robustness_active = "Robustness" in selected_params
        if hasattr(self, 'robustness_group'):
            self.robustness_group.setVisible(is_robustness_active)

        # Dynamic parameter row builder with specific, high-fidelity GMP explanations
        rows_html = ""
        for param in selected_params:
            strategy = "Experimental parameters execution based on standard protocol rules."
            limits = "Evaluated limits meeting GMP/GLP rules."
            
            if param == "System Suitability":
                strategy = "Replicate injections of standard preparation (n=5 or n=6)."
                limits = f"Area RSD ≤ {self.txt_limit_rsd.text()}, Peak Tailing ≤ {self.txt_limit_tailing.text()}."
            elif param == "Specificity":
                strategy = "Evaluate blank, placebo, standard, and spiked sample preparations."
                limits = "No interference at the retention time of the main analyte peak."
            elif param == "Linearity & Range":
                strategy = "Prepare and analyze minimum 5 concentration levels across the range."
                limits = "Correlation coefficient r² ≥ 0.999."
            elif param == "Accuracy (Recovery)":
                strategy = "Analyze spiked sample matrices at 3 levels (e.g., 80%, 100%, 120%) in triplicate."
                limits = f"Mean Recovery: {self.txt_limit_recovery.text()}."
            elif param == "Precision (Repeatability)":
                strategy = "Analyze 6 independent sample preparations at 100% target test concentration."
                limits = "RSD of assay results ≤ 2.0%."
            elif param == "Intermediate Precision":
                strategy = "Analyze replicate samples on different days, by different analysts, or different instruments."
                limits = "Cumulative RSD across both analysts/days ≤ 3.0%."
            elif param == "LOD":
                strategy = "Determine Limit of Detection via Signal-to-Noise (S/N ratio of 3:1) or slope method."
                limits = "Peak visually detectable and distinguishable from baseline noise."
            elif param == "LOQ":
                strategy = "Determine Limit of Quantitation via Signal-to-Noise (S/N ratio of 10:1) or slope method."
                limits = "Quantifiable with RSD ≤ 10.0%."
            elif param == "Robustness":
                robust_strategy = self.cmb_robustness_type.currentText()
                # Enhanced strategy based on selection type
                if "OFAT" in robust_strategy and "Both" not in robust_strategy:
                    strategy = f"Slight variation of critical parameters using <b>{robust_strategy}</b> model design. Each parameter varied individually (n=3 replicates per condition) while maintaining all other parameters at nominal values."
                    limits = "System suitability parameters remain compliant at both low and high levels of each tested parameter."
                elif "Full Factorial" in robust_strategy:
                    strategy = f"Partial Factorial DOE design using <b>{robust_strategy}</b> approach. Multi-variable parameter changes with statistical analysis of main effects and interactions using ANOVA."
                    limits = "Factors with statistical significance (p < 0.05) are identified. Effect estimates indicate the magnitude of each parameter's impact on method performance."
                elif "Both" in robust_strategy:
                    strategy = f"Combined <b>{robust_strategy}</b> approach: OFAT screening (individual parameter variations) followed by DOE analysis (multi-variable interactions and statistical significance)."
                    limits = "OFAT: individual parameter sensitivity identified. DOE: statistical significance (p < 0.05) and interaction effects quantified."

            rows_html += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="padding: 6px; border: 1px solid #CBD5E1; font-weight: bold; color: #1E3A8A; font-size: 10px;">{param}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E1; font-size: 10px; color: #334155;">{strategy}</td>
                <td style="padding: 6px; border: 1px solid #CBD5E1; font-size: 10px; color: #0F172A;">{limits}</td>
            </tr>
            """

        # Dynamic HPLC parameter block representation
        hplc_block_html = ""
        if self.chk_is_hplc.isChecked():
            hplc_block_html = f"""
            <h3 style="color: #0F172A; font-size: 12px; margin-top: 15px;">5.3 Chromatographic Setup Conditions</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 5px; font-size: 10px;">
                <tr style="background-color: #F1F5F9;">
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold; width: 40%;">Analytical Column:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_column.text()}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold;">Flow Rate Limit:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_flow.text()}</td>
                </tr>
                <tr style="background-color: #F1F5F9;">
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold;">Column Temperature:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_temp.text()}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold;">Detection Wavelength:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_wavelength.text()}</td>
                </tr>
                <tr style="background-color: #F1F5F9;">
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold;">Injection Volume:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_inj_vol.text()}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; border: 1px solid #CBD5E1; font-weight: bold;">Mobile Phase Composition:</td>
                    <td style="padding: 5px; border: 1px solid #CBD5E1;">{self.txt_mobile.text()}</td>
                </tr>
            </table>
            """

        # Dynamic Robustness Section Narrative - VERSATILE EXPLANATORY CONTENT
        robustness_block_html = ""
        if is_robustness_active:
            robust_type = self.cmb_robustness_type.currentText()
            include_table = self.chk_robustness_variables.isChecked()
            
            # Determine method type
            is_ofat = "OFAT" in robust_type and "Both" not in robust_type
            is_doe = "Full Factorial" in robust_type
            is_both = "Both" in robust_type
            
            # Build EXPLANATORY description based on method - NO HARDCODED VALUES
            if is_ofat:
                desc = (
                    "The OFAT (One Factor at a Time) approach evaluates robustness by varying one chromatographic parameter "
                    "at a time while keeping all other conditions constant. For each selected parameter, the analyst will: "
                    "1) Define a nominal (target) value, 2) Establish low and high variation limits (e.g., ±5% or ±2 units), "
                    "3) Perform replicate analyses (n=3) at each level, 4) Compare system suitability parameters against "
                    "acceptance criteria at both extremes. This identifies which individual parameters have the greatest "
                    "impact on method performance."
                )
                method_label = "OFAT (One Factor at a Time)"
            elif is_doe:
                desc = (
                    "The DOE (Design of Experiments) approach uses a Partial Factorial design to simultaneously evaluate "
                    "multiple parameters and their interactions. The analyst will: 1) Select 3-4 critical parameters, "
                    "2) Define low (-1) and high (+1) levels for each, 3) Execute a fractional factorial design matrix "
                    "(e.g., 2^(k-1) runs where k = number of factors), 4) Analyze and calculate: "
                    "Main effects (individual parameter impact), Two-way interactions (combined parameter effects), "
                    "Statistical significance (p-values). This identifies both individual and combined parameter effects."
                )
                method_label = "Partial Factorial DOE"
            elif is_both:
                desc = (
                    "This combined approach provides comprehensive robustness characterization in two phases: "
                    "PHASE 1 - OFAT Screening: Each parameter is varied individually (n=3 replicates per level) to "
                    "identify sensitive parameters. PHASE 2 - DOE Analysis: A Partial Factorial design is applied to "
                    "the identified critical parameters to quantify main effects, interaction effects, and statistical "
                    "This dual approach ensures both individual sensitivity and combined interaction effects are"
                    "thoroughly evaluated."
                )
                method_label = "OFAT + Partial Factorial DOE"
            else:
                desc = "Robustness evaluation will be performed according to ICH Q2(R1) guidelines."
                method_label = "Standard Approach"
            
            robustness_block_html = f"""
            <h3 style="color: #0F172A; font-size: 12px; margin-top: 15px;">5.4 Robustness Experimental Design</h3>
            <p style="color: #475569; font-size: 10px; line-height: 1.5; margin-top: 2px;">
                <b>Selected Evaluation Model:</b> {method_label}
            </p>
            <p style="color: #475569; font-size: 10px; line-height: 1.5; margin-top: 5px;">
                {desc}
            </p>
            """
            
            # Add EXPLANATORY parameters table if checked - NO HARDCODED VALUES
            if include_table:
                # Get current parameter values from UI for context
                current_flow = self.txt_flow.text()
                current_temp = self.txt_temp.text()
                current_column = self.txt_column.text()
                current_mobile = self.txt_mobile.text()
                current_wavelength = self.txt_wavelength.text()
                
                # OFAT EXPLANATORY TABLE
                if is_ofat or is_both:
                    robustness_block_html += """
                    <p style="color: #475569; font-size: 9px; margin-top: 8px;"><b>OFAT Experimental Design Guide:</b></p>
                    <p style="color: #64748B; font-size: 8.5px; margin-top: 2px; font-style: italic;">
                        For each parameter below, perform independent experiments at the defined levels while keeping all other parameters at nominal values.
                        Record system suitability parameters (RSD, tailing, resolution) at each level to determine sensitivity.
                    </p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 3px; font-size: 9px;">
                        <tr style="background-color: #1E3A8A; color: white;">
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 30%;">Parameter</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Nominal Value</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Low Level</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 20%;">High Level</th>
                        </tr>
                        <tr>
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Mobile Phase Ratio</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">{current_mobile if current_mobile else "User Defined"}</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 5% (adjust composition)</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 5% (adjust composition)</td>
                        </tr>
                        <tr style="background-color: #F8FAFC;">
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Flow Rate</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">{current_flow if current_flow else "User Defined"}</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 0.2 mL/min</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 0.2 mL/min</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Column Temperature</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">{current_temp if current_temp else "User Defined"}</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 2°C</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 2°C</td>
                        </tr>
                        <tr style="background-color: #F8FAFC;">
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Detection Wavelength</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">{current_wavelength if current_wavelength else "User Defined"}</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 2 nm</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 2 nm</td>
                        </tr>
                    </table>
                    <p style="color: #64748B; font-size: 8px; margin-top: 3px; font-style: italic;">
                        <b>Evaluation:</b> At each level, verify that system suitability criteria (RSD ≤ {self.txt_limit_rsd.text()}, 
                        Tailing ≤ {self.txt_limit_tailing.text()}) are met. Document any significant changes in performance.
                    </p>
                    """
                
                # DOE EXPLANATORY TABLE
                if is_doe or is_both:
                    if is_both:
                        robustness_block_html += """
                        <p style="color: #475569; font-size: 9px; margin-top: 10px;"><b>DOE Experimental Design Guide:</b></p>
                        """
                    else:
                        robustness_block_html += """
                        <p style="color: #475569; font-size: 9px; margin-top: 8px;"><b>DOE Partial Factorial Design Guide:</b></p>
                        """
                    
                    robustness_block_html += """
                    <p style="color: #64748B; font-size: 8.5px; margin-top: 2px; font-style: italic;">
                        Execute a 2^(k-1) fractional factorial design where k = number of factors. Each run is performed in duplicate.
                        Analyze results using ANOVA to identify significant factors and interactions (p < 0.05).
                    </p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 3px; font-size: 9px;">
                        <tr style="background-color: #1E3A8A; color: white;">
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Factor</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Low Level (-1)</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">High Level (+1)</th>
                            <th style="padding: 4px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Analysis Goal</th>
                        </tr>
                        <tr>
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Factor A: Mobile Phase</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 5%</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 5%</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate main effect</td>
                        </tr>
                        <tr style="background-color: #F8FAFC;">
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Factor B: Flow Rate</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 0.2 mL/min</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 0.2 mL/min</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate main effect</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Factor C: Temperature</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal - 2°C</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Nominal + 2°C</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate main effect</td>
                        </tr>
                        <tr style="background-color: #F8FAFC;">
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Interaction AB</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;" colspan="2">Combined effect of A and B</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate interaction effect</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Interaction AC</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;" colspan="2">Combined effect of A and C</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate interaction effect</td>
                        </tr>
                        <tr style="background-color: #F8FAFC;">
                            <td style="padding: 4px; border: 1px solid #CBD5E1; font-weight: bold;">Interaction BC</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;" colspan="2">Combined effect of B and C</td>
                            <td style="padding: 4px; border: 1px solid #CBD5E1;">Calculate interaction effect</td>
                        </tr>
                    </table>
                    <p style="color: #64748B; font-size: 8px; margin-top: 3px; font-style: italic;">
                        <b>Statistical Analysis:</b> Perform ANOVA to identify significant factors (p < 0.05). 
                        Factors with p < 0.05 are considered statistically significant. Effect estimates indicate the magnitude of impact 
                        on method performance (e.g., recovery %, retention time, peak area).
                    </p>
                    """
                
                if is_both:
                    robustness_block_html += """
                    <p style="color: #64748B; font-size: 8px; margin-top: 5px; font-style: italic;">
                        <b>Note:</b> This combined approach provides comprehensive robustness characterization. 
                        Use OFAT results to identify sensitive parameters, then apply DOE to these parameters 
                        to quantify interactions and statistical significance for method optimization.
                    </p>
                    """

        preview_html = f"""
        <div style="font-family: 'Helvetica', sans-serif; padding: 10px;">
            <p style="color: #64748B; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin: 0;">🏢 {company}</p>
            <h1 style="color: #1E3A8A; margin-top: 3px; margin-bottom: 0px; font-size: 17px;">METHOD {study_type.upper()} PROTOCOL ({test_type.upper()})</h1>
            <p style="color: #475569; font-size: 10px; margin-top: 2px;">Document Reference Code: <b>{protocol}</b></p>
            <hr style="border: 0px; border-top: 1.5px solid #1E3A8A; margin-bottom: 12px;" />
            
            <h3 style="color: #0F172A; font-size: 12px; margin-top: 10px;">1.0 Objective</h3>
            <p style="color: #475569; font-size: 10.5px; line-height: 1.4; margin-top: 3px;">
                To establish documentary evidence to confirm that the analytical procedure for measuring {test_type.lower()} content yields consistent results.
            </p>

            <h3 style="color: #0F172A; font-size: 12px; margin-top: 15px;">5.0 Prep Methodology</h3>
            <p style="color: #334155; font-size: 10px; margin-top: 2px;"><b>5.1 Standard Preparation:</b><br/>{self.txt_std_prep.toPlainText() if self.txt_std_prep.toPlainText() else "<i>Pending standard preparation input...</i>"}</p>
            <p style="color: #334155; font-size: 10px; margin-top: 5px;"><b>5.2 Sample Preparation:</b><br/>{self.txt_sample_prep.toPlainText() if self.txt_sample_prep.toPlainText() else "<i>Pending sample preparation input...</i>"}</p>
            
            {hplc_block_html}

            {robustness_block_html}

            <h3 style="color: #0F172A; font-size: 12px; margin-top: 15px;">6.0 Calculation Formulas</h3>
            <p style="background-color: #F8FAFC; padding: 6px; border-left: 3px solid #1E3A8A; font-family: monospace; font-size: 10px; color: #1E293B;">
                {self.txt_formula.toPlainText()}
            </p>
            <p style="font-size: 9.5px; color: #475569; white-space: pre-line;">{self.txt_formula_defs.toPlainText()}</p>

            <h3 style="color: #0F172A; font-size: 12px; margin-top: 15px;">7.0 Parameter Acceptance Thresholds</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 5px; font-size: 10px;">
                <tr style="background-color: #1E3A8A; color: white;">
                    <th style="padding: 5px; border: 1px solid #CBD5E1; text-align: left; width: 25%;">Parameter</th>
                    <th style="padding: 5px; border: 1px solid #CBD5E1; text-align: left; width: 45%;">Strategy</th>
                    <th style="padding: 5px; border: 1px solid #CBD5E1; text-align: left; width: 30%;">Acceptance Criteria Limits</th>
                </tr>
                {rows_html}
            </table>
        </div>
        """
        self.preview_browser.setHtml(preview_html)

    def export_protocol_pdf(self):
        if not self.active_project_data:
            return

        protocol_ref = self.active_project_data[5]
        study_type = "Validation" if self.rad_validation.isChecked() else "Verification"
        test_type = self.cmb_test_type.currentText()
        default_filename = f"{protocol_ref}_{study_type}_{test_type.replace(' ', '_')}_Protocol.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Protocol PDF", default_filename, "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                # Build survey data with robustness information
                survey_data = {
                    "company_name": self.txt_company.text(),
                    "study_type": study_type,
                    "test_type": test_type,
                    "parameters": self.get_selected_parameters(),
                    "std_prep": self.txt_std_prep.toPlainText(),
                    "sample_prep": self.txt_sample_prep.toPlainText(),
                    "is_hplc": self.chk_is_hplc.isChecked(),
                    "hplc_column": self.txt_column.text(),
                    "hplc_flow": self.txt_flow.text(),
                    "hplc_temp": self.txt_temp.text(),
                    "hplc_wavelength": self.txt_wavelength.text(),
                    "hplc_inj_vol": self.txt_inj_vol.text(),
                    "hplc_mobile": self.txt_mobile.text(),
                    "formula_text": self.txt_formula.toPlainText(),
                    "formula_defs": self.txt_formula_defs.toPlainText(),
                    "limit_rsd": self.txt_limit_rsd.text(),
                    "limit_tailing": self.txt_limit_tailing.text(),
                    "limit_recovery": self.txt_limit_recovery.text(),
                    # Export robustness selection and optional table toggle
                    "robustness_type": self.cmb_robustness_type.currentText() if "Robustness" in self.get_selected_parameters() else None,
                    "robustness_include_table": self.chk_robustness_variables.isChecked() if "Robustness" in self.get_selected_parameters() else False
                }

                generate_assay_pdf(file_path, self.active_project_data, survey_data)
                
                QMessageBox.information(
                    self, "Success", f"Customized {test_type} Protocol successfully generated!\nPath: {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "PDF Compile Error", f"An unexpected compile exception occurred:\n{str(e)}"
                )