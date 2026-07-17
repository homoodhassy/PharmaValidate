"""
PharmaValidate v0.5 - Related Substances Linearity & RRF Sub-module
Provides an interactive table for analytical chemists to input calibration standard responses
for both Active Drug Substance and the target Impurity to calculate slopes, R^2, and RRF.
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

class RelSubLinearityWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_imp = None
        self.db = RelSubDatabase()
        
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Main Info Label
        self.lbl_title = QLabel("📈 Linearity & Relative Response Factor (RRF) Study")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        main_layout.addWidget(self.lbl_title)

        # Core Split Layout (Left: Data Entry Table | Right: Calculations & Results)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # ==========================================
        # LEFT SIDE: DATA TABLE CONTAINER
        # ==========================================
        left_container = QFrame()
        left_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        left_layout.addWidget(QLabel("<b>Calibration Curve Data Points:</b>"))

        # Interactive grid table
        self.table = QTableWidget(6, 5) # Default 6 levels of concentration
        self.table.setHorizontalHeaderLabels([
            "Level", 
            "Active Conc\n(µg/mL)", 
            "Active Area\n(counts)", 
            "Impurity Conc\n(µg/mL)", 
            "Impurity Area\n(counts)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #E2E8F0; border: 1px solid #E2E8F0; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; border: 1px solid #E2E8F0; }
        """)
        
        self.initialize_empty_table()
        left_layout.addWidget(self.table)

        # Table Control Buttons
        table_buttons = QHBoxLayout()
        self.btn_add_row = QPushButton("+ Add Level")
        self.btn_add_row.clicked.connect(self.add_row)
        self.btn_add_row.setStyleSheet("background-color: #F1F5F9; color: #1E293B; border: 1px solid #CBD5E1; padding: 5px 10px; border-radius: 4px;")
        
        self.btn_remove_row = QPushButton("- Remove Level")
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
        # RIGHT SIDE: RESULTS CARD
        # ==========================================
        right_container = QFrame()
        right_container.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        right_layout.addWidget(QLabel("<h3 style='color:#1E3A8A; margin:0;'>Linear Regression Statistics</h3>"))

        # Results Grid Display
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(12)

        # Active curve labels
        stats_layout.addWidget(QLabel("<b>Active Drug Substance:</b>"), 0, 0, 1, 2)
        self.lbl_act_slope = QLabel("Slope (m): -")
        self.lbl_act_intercept = QLabel("Intercept (c): -")
        self.lbl_act_r2 = QLabel("R²: -")
        stats_layout.addWidget(self.lbl_act_slope, 1, 0)
        stats_layout.addWidget(self.lbl_act_intercept, 1, 1)
        stats_layout.addWidget(self.lbl_act_r2, 2, 0)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E2E8F0;")
        stats_layout.addWidget(line, 3, 0, 1, 2)

        # Impurity curve labels
        stats_layout.addWidget(QLabel("<b>Target Impurity:</b>"), 4, 0, 1, 2)
        self.lbl_imp_slope = QLabel("Slope (m): -")
        self.lbl_imp_intercept = QLabel("Intercept (c): -")
        self.lbl_imp_r2 = QLabel("R²: -")
        stats_layout.addWidget(self.lbl_imp_slope, 5, 0)
        stats_layout.addWidget(self.lbl_imp_intercept, 5, 1)
        stats_layout.addWidget(self.lbl_imp_r2, 6, 0)

        right_layout.addWidget(stats_frame)

        # RRF Output Callout Box
        rrf_box = QFrame()
        rrf_box.setStyleSheet("background-color: #EFF6FF; border: 1.5px dashed #3B82F6; border-radius: 6px; padding: 10px;")
        rrf_box_layout = QVBoxLayout(rrf_box)
        self.lbl_calculated_rrf = QLabel("Calculated RRF: N/A")
        self.lbl_calculated_rrf.setStyleSheet("font-size: 16px; font-weight: bold; color: #1D4ED8; text-align: center;")
        rrf_box_layout.addWidget(self.lbl_calculated_rrf)
        right_layout.addWidget(rrf_box)

        # Main Action Buttons
        self.btn_calculate = QPushButton("Calculate Regression & RRF")
        self.btn_calculate.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border:none;")
        self.btn_calculate.clicked.connect(self.calculate_regression_and_rrf)
        right_layout.addWidget(self.btn_calculate)

        self.btn_save_data = QPushButton("Save Linearity Dataset")
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
        """Pre-populates basic numeric labels for levels to guide input."""
        for row in range(self.table.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Level index read-only
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)

    def add_row(self):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        level_item = QTableWidgetItem(str(row_idx + 1))
        level_item.setFlags(level_item.flags() & ~Qt.ItemIsEditable)
        level_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row_idx, 0, level_item)

    def remove_row(self):
        row_count = self.table.rowCount()
        if row_count > 2:  # Must have at least two points for regression
            self.table.removeRow(row_count - 1)

    def clear_table_data(self):
        for r in range(self.table.rowCount()):
            for c in range(1, 5):
                self.table.setItem(r, c, None)
        self.clear_stats_labels()

    def clear_stats_labels(self):
        self.lbl_act_slope.setText("Slope (m): -")
        self.lbl_act_intercept.setText("Intercept (c): -")
        self.lbl_act_r2.setText("R²: -")
        self.lbl_imp_slope.setText("Slope (m): -")
        self.lbl_imp_intercept.setText("Intercept (c): -")
        self.lbl_imp_r2.setText("R²: -")
        self.lbl_calculated_rrf.setText("Calculated RRF: N/A")

    # ==========================================
    # DATA PROPAGATION FROM WORKSPACE
    # ==========================================
    def set_active_impurity(self, profile):
        """Loads calibration curve points from SQLite database when the selected impurity shifts."""
        self.active_imp = profile
        self.clear_table_data()

        if not profile:
            self.lbl_title.setText("📈 Linearity & Relative Response Factor (RRF) Study")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.lbl_title.setText(f"📈 Linearity & RRF Study for: {profile['name']} (Spec Limit: {profile['spec_limit']}%)")

        # Load raw data run matrix from Database
        runs = self.db.get_linearity_runs(profile["id"])
        if len(runs) > 0:
            self.table.setRowCount(0)
            for idx, (level_num, act_c, act_a, imp_c, imp_a) in enumerate(runs):
                self.table.insertRow(idx)
                
                # Level item
                lvl_item = QTableWidgetItem(str(level_num))
                lvl_item.setFlags(lvl_item.flags() & ~Qt.ItemIsEditable)
                lvl_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(idx, 0, lvl_item)

                # Active Conc
                self.table.setItem(idx, 1, QTableWidgetItem(str(act_c)))
                # Active Area
                self.table.setItem(idx, 2, QTableWidgetItem(str(act_a)))
                # Imp Conc
                self.table.setItem(idx, 3, QTableWidgetItem(str(imp_c)))
                # Imp Area
                self.table.setItem(idx, 4, QTableWidgetItem(str(imp_a)))
            
            # Immediately trigger regression updates for loaded values
            self.calculate_regression_and_rrf(silent=True)
        else:
            # Set up 6 blank levels
            self.table.setRowCount(6)
            self.initialize_empty_table()

    # ==========================================
    # MATHEMATICAL CALCULATIONS
    # ==========================================
    def get_parsed_data(self):
        """Extracts and parses float inputs from UI data grid."""
        active_x, active_y = [], []
        impurity_x, impurity_y = [], []
        raw_rows = []

        for row in range(self.table.rowCount()):
            try:
                # Level
                level_txt = self.table.item(row, 0).text()
                level_num = int(level_txt)

                # Parse inputs safely
                act_c_item = self.table.item(row, 1)
                act_a_item = self.table.item(row, 2)
                imp_c_item = self.table.item(row, 3)
                imp_a_item = self.table.item(row, 4)

                # Row must contain fully filled data to be evaluated
                if act_c_item and act_a_item and imp_c_item and imp_a_item:
                    act_c = float(act_c_item.text())
                    act_a = float(act_a_item.text())
                    imp_c = float(imp_c_item.text())
                    imp_a = float(imp_a_item.text())

                    active_x.append(act_c)
                    active_y.append(act_a)
                    impurity_x.append(imp_c)
                    impurity_y.append(imp_a)

                    raw_rows.append((level_num, act_c, act_a, imp_c, imp_a))
            except (AttributeError, ValueError):
                continue  # Skip row if partially empty or invalid numeric strings

        return active_x, active_y, impurity_x, impurity_y, raw_rows

    def calculate_regression_and_rrf(self, silent=False):
        """Triggers mathematical solver to extract statistical parameters."""
        act_x, act_y, imp_x, imp_y, _ = self.get_parsed_data()

        if len(act_x) < 2 or len(imp_x) < 2:
            if not silent:
                QMessageBox.warning(self, "Data Error", "Please fill in at least 2 complete concentration levels to run regression.")
            return

        # Solve regressions
        res_active = RelSubCalculator.calculate_regression(act_x, act_y)
        res_impurity = RelSubCalculator.calculate_regression(imp_x, imp_y)
        
        # Determine RRF
        rrf = RelSubCalculator.calculate_rrf(res_impurity["slope"], res_active["slope"])

        # Display results to user
        self.lbl_act_slope.setText(f"Slope (m): {res_active['slope']:.4f}")
        self.lbl_act_intercept.setText(f"Intercept (c): {res_active['intercept']:.2f}")
        self.lbl_act_r2.setText(f"R²: {res_active['r_squared']:.5f}")

        self.lbl_imp_slope.setText(f"Slope (m): {res_impurity['slope']:.4f}")
        self.lbl_imp_intercept.setText(f"Intercept (c): {res_impurity['intercept']:.2f}")
        self.lbl_imp_r2.setText(f"R²: {res_impurity['r_squared']:.5f}")

        self.lbl_calculated_rrf.setText(f"Calculated RRF: {rrf:.4f}")

    # ==========================================
    # SAVE DATA PERSISTENCE
    # ==========================================
    def save_data_to_db(self):
        """Saves current table entries directly into the SQLite database."""
        if not self.active_imp:
            return

        act_x, act_y, imp_x, imp_y, raw_rows = self.get_parsed_data()

        if len(raw_rows) == 0:
            QMessageBox.warning(self, "Validation Error", "No valid numeric data points found to save.")
            return

        # Save to SQLite database
        self.db.save_linearity_runs(self.active_imp["id"], raw_rows)

        # If a valid regression has run, save calculated RRF back to the impurity config!
        if len(act_x) >= 2 and len(imp_x) >= 2:
            res_active = RelSubCalculator.calculate_regression(act_x, act_y)
            res_impurity = RelSubCalculator.calculate_regression(imp_x, imp_y)
            rrf_val = RelSubCalculator.calculate_rrf(res_impurity["slope"], res_active["slope"])
            
            # Update configuration in db (applying current RRF update)
            self.db.update_impurity_config(
                impurity_id=self.active_imp["id"],
                spec_limit=self.active_imp["spec_limit"],
                use_rrf=True,
                rrf_value=float(f"{rrf_val:.4f}")
            )

        QMessageBox.information(self, "Success", "Linearity dataset saved successfully!")