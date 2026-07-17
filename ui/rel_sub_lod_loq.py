"""
PharmaValidate v0.5 - Related Substances LOD & LOQ Verification Sub-module
Allows verifying chromatographic sensitivity limits via Signal-to-Noise (S/N) input, 
or by automatically importing regression results from the Linearity study.
"""

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PySide6.QtCore import Qt

# Import backend dependencies
from database.rel_sub_db import RelSubDatabase
from calculations.rel_sub_calculator import RelSubCalculator

class RelSubLodLoqWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_imp = None
        self.db = RelSubDatabase()
        
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Module Header
        self.lbl_title = QLabel("🧬 Sensitivity Study (LOD & LOQ Determination)")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        main_layout.addWidget(self.lbl_title)

        # Split Layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # ==========================================
        # LEFT CONTAINER: SIGNAL-TO-NOISE INPUTS
        # ==========================================
        left_container = QFrame()
        left_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        left_layout.addWidget(QLabel("<b>Method A: Signal-to-Noise (S/N) Verification</b>"))
        left_layout.addWidget(QLabel("<small style='color:#64748B;'>Enter replicate concentrations injected near limit concentrations with their HPLC S/N ratios.</small>"))

        # Data Entry Grid
        self.table = QTableWidget(5, 3) # Default 5 levels of S/N evaluation
        self.table.setHorizontalHeaderLabels(["Injection Run", "Concentration\n(µg/mL)", "Signal-to-Noise\n(S/N) Ratio"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #E2E8F0; border: 1px solid #E2E8F0; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; border: 1px solid #E2E8F0; }
        """)
        
        self.initialize_empty_table()
        left_layout.addWidget(self.table)

        # Table Row Control Buttons
        table_buttons = QHBoxLayout()
        self.btn_add_row = QPushButton("+ Add Run")
        self.btn_add_row.clicked.connect(self.add_row)
        self.btn_add_row.setStyleSheet("background-color: #F1F5F9; color: #1E293B; border: 1px solid #CBD5E1; padding: 5px 10px; border-radius: 4px;")
        
        self.btn_remove_row = QPushButton("- Remove Run")
        self.btn_remove_row.clicked.connect(self.remove_row)
        self.btn_remove_row.setStyleSheet("background-color: #F1F5F9; color: #EF4444; border: 1px solid #FCA5A5; padding: 5px 10px; border-radius: 4px;")

        self.btn_clear = QPushButton("Clear Grid")
        self.btn_clear.clicked.connect(self.clear_table_data)
        self.btn_clear.setStyleSheet("background-color: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; padding: 5px 10px; border-radius: 4px;")

        table_buttons.addWidget(self.btn_add_row)
        table_buttons.addWidget(self.btn_remove_row)
        table_buttons.addStretch()
        table_buttons.addWidget(self.btn_clear)
        left_layout.addLayout(table_buttons)

        split_layout.addWidget(left_container, stretch=3)

        # ==========================================
        # RIGHT CONTAINER: METHOD CALCULATION CARDS
        # ==========================================
        right_container = QFrame()
        right_container.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        right_layout.addWidget(QLabel("<h3 style='color:#1E3A8A; margin:0;'>LOD/LOQ Assessment Results</h3>"))

        # Section 1: S/N Based Calculation Output
        sn_card = QFrame()
        sn_card.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px;")
        sn_card_layout = QVBoxLayout(sn_card)
        sn_card_layout.setSpacing(8)
        sn_card_layout.addWidget(QLabel("<b>Method A Results (S/N Targets):</b>"))
        
        self.lbl_sn_lod = QLabel("LOD Target (S/N ≥ 3): -")
        self.lbl_sn_loq = QLabel("LOQ Target (S/N ≥ 10): -")
        self.lbl_sn_lod.setStyleSheet("color: #334155;")
        self.lbl_sn_loq.setStyleSheet("color: #334155;")
        
        sn_card_layout.addWidget(self.lbl_sn_lod)
        sn_card_layout.addWidget(self.lbl_sn_loq)
        right_layout.addWidget(sn_card)

        # Section 2: Linearity Curve Statistical Estimation Output
        reg_card = QFrame()
        reg_card.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px;")
        reg_card_layout = QVBoxLayout(reg_card)
        reg_card_layout.setSpacing(8)
        reg_card_layout.addWidget(QLabel("<b>Method B Results (Linearity Curve Statistics):</b>"))
        
        self.lbl_reg_slope = QLabel("Impurity Slope: -")
        self.lbl_reg_lod = QLabel("Theoretical LOD (3.3 σ/S): -")
        self.lbl_reg_loq = QLabel("Theoretical LOQ (10 σ/S): -")
        
        reg_card_layout.addWidget(self.lbl_reg_slope)
        reg_card_layout.addWidget(self.lbl_reg_lod)
        reg_card_layout.addWidget(self.lbl_reg_loq)
        right_layout.addWidget(reg_card)

        # Action Buttons
        self.btn_calculate = QPushButton("Calculate Sensitivity Limits")
        self.btn_calculate.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border:none;")
        self.btn_calculate.clicked.connect(self.calculate_lod_loq)
        right_layout.addWidget(self.btn_calculate)

        self.btn_save_data = QPushButton("Save S/N Verification Run")
        self.btn_save_data.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border:none;")
        self.btn_save_data.clicked.connect(self.save_data_to_db)
        right_layout.addWidget(self.btn_save_data)

        right_layout.addStretch()
        split_layout.addWidget(right_container, stretch=2)

        main_layout.addLayout(split_layout)

    # ==========================================
    # GRID INTERACTION METHODS
    # ==========================================
    def initialize_empty_table(self):
        for row in range(self.table.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)

    def add_row(self):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        run_item = QTableWidgetItem(str(row_idx + 1))
        run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
        run_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row_idx, 0, run_item)

    def remove_row(self):
        row_count = self.table.rowCount()
        if row_count > 1:
            self.table.removeRow(row_count - 1)

    def clear_table_data(self):
        for r in range(self.table.rowCount()):
            for c in range(1, 3):
                self.table.setItem(r, c, None)
        self.clear_stats_labels()

    def clear_stats_labels(self):
        self.lbl_sn_lod.setText("LOD Target (S/N ≥ 3): -")
        self.lbl_sn_loq.setText("LOQ Target (S/N ≥ 10): -")

    # ==========================================
    # STATE / SYNERGY SYSTEM LOADERS
    # ==========================================
    def set_active_impurity(self, profile):
        """Loads verification runs and theoretical calculations immediately upon selected impurity switch."""
        self.active_imp = profile
        self.clear_table_data()
        
        # Reset regression stats card
        self.lbl_reg_slope.setText("Impurity Slope: -")
        self.lbl_reg_lod.setText("Theoretical LOD (3.3 σ/S): -")
        self.lbl_reg_loq.setText("Theoretical LOQ (10 σ/S): -")

        if not profile:
            self.lbl_title.setText("🧬 Sensitivity Study (LOD & LOQ Determination)")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.lbl_title.setText(f"🧬 Sensitivity Study for: {profile['name']} (Spec Limit: {profile['spec_limit']}%)")

        # 1. Load Signal-To-Noise data points if they exist in SQLite database
        runs = self.db.get_lod_loq_runs(profile["id"])
        if len(runs) > 0:
            self.table.setRowCount(0)
            for idx, (run_num, conc, sn) in enumerate(runs):
                self.table.insertRow(idx)
                
                run_item = QTableWidgetItem(str(run_num))
                run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
                run_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(idx, 0, run_item)

                self.table.setItem(idx, 1, QTableWidgetItem(str(conc)))
                self.table.setItem(idx, 2, QTableWidgetItem(str(sn)))
            self.calculate_sn_limits()
        else:
            self.table.setRowCount(5)
            self.initialize_empty_table()

        # 2. CALCULATE METHOD B: Synergize regression details from Linearity
        self.calculate_theoretical_limits_from_linearity()

    def calculate_theoretical_limits_from_linearity(self):
        """Fetches the Linearity database runs to calculate regression parameters for Method B."""
        if not self.active_imp:
            return

        lin_runs = self.db.get_linearity_runs(self.active_imp["id"])
        if len(lin_runs) < 2:
            self.lbl_reg_slope.setText("Impurity Slope: Linearity data missing")
            return

        # Extract impurity concentrations and peak areas
        imp_concs = [row[3] for row in lin_runs]
        imp_areas = [row[4] for row in lin_runs]

        # Calculate regression using mathematical core
        res = RelSubCalculator.calculate_regression(imp_concs, imp_areas)
        
        # Determine limits using residual standard deviation standard error
        limits = RelSubCalculator.calculate_lod_loq_from_curve(res["slope"], res["intercept_std_dev"])

        self.lbl_reg_slope.setText(f"Impurity Slope (S): {res['slope']:.4f}")
        self.lbl_reg_lod.setText(f"Theoretical LOD (3.3 σ/S): {limits['lod']:.4f} µg/mL")
        self.lbl_reg_loq.setText(f"Theoretical LOQ (10 σ/S): {limits['loq']:.4f} µg/mL")

    # ==========================================
    # MATH COMPUTATION & VERIFICATION
    # ==========================================
    def get_parsed_data(self):
        concs = []
        sn_ratios = []
        raw_rows = []

        for row in range(self.table.rowCount()):
            try:
                run_txt = self.table.item(row, 0).text()
                run_num = int(run_txt)

                conc_item = self.table.item(row, 1)
                sn_item = self.table.item(row, 2)

                if conc_item and sn_item:
                    conc = float(conc_item.text())
                    sn = float(sn_item.text())
                    
                    concs.append(conc)
                    sn_ratios.append(sn)
                    raw_rows.append((run_num, conc, sn))
            except (AttributeError, ValueError):
                continue

        return concs, sn_ratios, raw_rows

    def calculate_sn_limits(self):
        """Interrogates standard signal-to-noise thresholds."""
        concs, sn_ratios, _ = self.get_parsed_data()
        if len(concs) == 0:
            return

        res = RelSubCalculator.calculate_lod_loq_by_sn(concs, sn_ratios)
        
        lod_text = f"{res['lod']:.4f} µg/mL" if res['lod'] is not None else "Not Detected (No Run ≥ 3.0)"
        loq_text = f"{res['loq']:.4f} µg/mL" if res['loq'] is not None else "Not Quantified (No Run ≥ 10.0)"

        self.lbl_sn_lod.setText(f"LOD Target (S/N ≥ 3): {lod_text}")
        self.lbl_sn_loq.setText(f"LOQ Target (S/N ≥ 10): {loq_text}")

    def calculate_lod_loq(self):
        """Master button click calculator."""
        # Calculate Signal-to-Noise
        self.calculate_sn_limits()
        # Calculate Regression statistics again in case linearity has changed
        self.calculate_theoretical_limits_from_linearity()
        QMessageBox.information(self, "Calculations Complete", "Sensitivity evaluation limits calculated successfully.")

    # ==========================================
    # PERSIST DATA IN SQLITE
    # ==========================================
    def save_data_to_db(self):
        if not self.active_imp:
            return

        _, _, raw_rows = self.get_parsed_data()

        if len(raw_rows) == 0:
            QMessageBox.warning(self, "Validation Error", "No complete S/N data entries found to save.")
            return

        # Save to SQLite database
        self.db.save_lod_loq_runs(self.active_imp["id"], raw_rows)
        QMessageBox.information(self, "Success", "S/N Limit Verification run details successfully saved.")