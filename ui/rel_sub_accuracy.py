"""
PharmaValidate v0.5 - Related Substances Spiked Recovery (Accuracy) Sub-module
Manages high-fidelity accuracy data entry. Dynamically applies the linearity regression 
line of the active impurity to calculate found concentrations, individual recoveries, 
mean recovery, and %RSD across LOQ, 100%, and 150% levels.
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

class RelSubAccuracyWidget(QWidget):
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
        self.lbl_title = QLabel("🧪 Spiked Recovery (Accuracy) Verification Study")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        main_layout.addWidget(self.lbl_title)

        # Split Layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # ==========================================
        # LEFT SIDE: DATA ENTRY GRID (9 Replicates)
        # ==========================================
        left_container = QFrame()
        left_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        left_layout.addWidget(QLabel("<b>Spiked Accuracy Replicates:</b>"))
        left_layout.addWidget(QLabel("<small style='color:#64748B;'>Enter the spiked concentrations and peak areas. Calculated % Recovery uses the active impurity's linearity curve.</small>"))

        # 9-row grid (3 levels x 3 replicates)
        self.table = QTableWidget(9, 5)
        self.table.setHorizontalHeaderLabels([
            "Spike Level", 
            "Rep #", 
            "Spiked Conc\n(µg/mL)", 
            "Peak Area\n(counts)", 
            "Calculated\nRecovery (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #E2E8F0; border: 1px solid #E2E8F0; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; border: 1px solid #E2E8F0; }
        """)
        
        self.initialize_empty_table()
        left_layout.addWidget(self.table)

        # Control Buttons
        table_buttons = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Grid")
        self.btn_clear.clicked.connect(self.clear_table_data)
        self.btn_clear.setStyleSheet("background-color: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; padding: 5px 15px; border-radius: 4px;")
        table_buttons.addStretch()
        table_buttons.addWidget(self.btn_clear)
        left_layout.addLayout(table_buttons)

        split_layout.addWidget(left_container, stretch=3)

        # ==========================================
        # RIGHT SIDE: SUMMARY RESULTS STATISTICS
        # ==========================================
        right_container = QFrame()
        right_container.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        right_layout.addWidget(QLabel("<h3 style='color:#1E3A8A; margin:0;'>Accuracy Level Summary</h3>"))

        # Summary Grid Layout
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;")
        summary_layout = QGridLayout(summary_frame)
        summary_layout.setSpacing(15)

        # Labels for LOQ Level
        summary_layout.addWidget(QLabel("<b>LOQ Spike Level:</b>"), 0, 0, 1, 2)
        self.lbl_loq_mean = QLabel("Mean Recovery: -")
        self.lbl_loq_rsd = QLabel("Recovery RSD: -")
        summary_layout.addWidget(self.lbl_loq_mean, 1, 0)
        summary_layout.addWidget(self.lbl_loq_rsd, 1, 1)

        # Labels for 100% Level
        summary_layout.addWidget(QLabel("<b>100% Spike Level:</b>"), 2, 0, 1, 2)
        self.lbl_mid_mean = QLabel("Mean Recovery: -")
        self.lbl_mid_rsd = QLabel("Recovery RSD: -")
        summary_layout.addWidget(self.lbl_mid_mean, 3, 0)
        summary_layout.addWidget(self.lbl_mid_rsd, 3, 1)

        # Labels for 150% Level
        summary_layout.addWidget(QLabel("<b>150% Spike Level:</b>"), 4, 0, 1, 2)
        self.lbl_high_mean = QLabel("Mean Recovery: -")
        self.lbl_high_rsd = QLabel("Recovery RSD: -")
        summary_layout.addWidget(self.lbl_high_mean, 5, 0)
        summary_layout.addWidget(self.lbl_high_rsd, 5, 1)

        right_layout.addWidget(summary_frame)

        # Actions
        self.btn_calculate = QPushButton("Calculate Recovery Stats")
        self.btn_calculate.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border:none;")
        self.btn_calculate.clicked.connect(self.calculate_accuracy_suite)
        right_layout.addWidget(self.btn_calculate)

        self.btn_save = QPushButton("Save Accuracy Records")
        self.btn_save.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 10px; border-radius: 6px; border:none;")
        self.btn_save.clicked.connect(self.save_data_to_db)
        right_layout.addWidget(self.btn_save)

        right_layout.addStretch()
        split_layout.addWidget(right_container, stretch=2)

        main_layout.addLayout(split_layout)

    # ==========================================
    # GRID INTERACTION METHODS
    # ==========================================
    def initialize_empty_table(self):
        """Builds a structured layout of 3 levels with 3 replicates."""
        levels = ["LOQ", "LOQ", "LOQ", "100%", "100%", "100%", "150%", "150%", "150%"]
        reps = ["1", "2", "3", "1", "2", "3", "1", "2", "3"]

        for row in range(9):
            # Level Identifier
            lvl_item = QTableWidgetItem(levels[row])
            lvl_item.setFlags(lvl_item.flags() & ~Qt.ItemIsEditable)
            lvl_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, lvl_item)

            # Replicate Identifier
            rep_item = QTableWidgetItem(reps[row])
            rep_item.setFlags(rep_item.flags() & ~Qt.ItemIsEditable)
            rep_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, rep_item)

            # Recovery column read-only (it is calculated dynamically)
            rec_item = QTableWidgetItem("-")
            rec_item.setFlags(rec_item.flags() & ~Qt.ItemIsEditable)
            rec_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, rec_item)

    def clear_table_data(self):
        for r in range(9):
            self.table.setItem(r, 2, None)
            self.table.setItem(r, 3, None)
            
            rec_item = QTableWidgetItem("-")
            rec_item.setFlags(rec_item.flags() & ~Qt.ItemIsEditable)
            rec_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 4, rec_item)

        self.clear_stats_labels()

    def clear_stats_labels(self):
        self.lbl_loq_mean.setText("Mean Recovery: -")
        self.lbl_loq_rsd.setText("Recovery RSD: -")
        self.lbl_mid_mean.setText("Mean Recovery: -")
        self.lbl_mid_rsd.setText("Recovery RSD: -")
        self.lbl_high_mean.setText("Mean Recovery: -")
        self.lbl_high_rsd.setText("Recovery RSD: -")

    # ==========================================
    # STATE / SYNERGY DATA LOADERS
    # ==========================================
    def set_active_impurity(self, profile):
        """Loads recovery replicate raw values immediately when switching selected impurities."""
        self.active_imp = profile
        self.clear_table_data()

        if not profile:
            self.lbl_title.setText("🧪 Spiked Recovery (Accuracy) Verification Study")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.lbl_title.setText(f"🧪 Accuracy Study for: {profile['name']} (Spec Limit: {profile['spec_limit']}%)")

        # Load raw accuracy levels from database
        runs = self.db.get_accuracy_runs(profile["id"])
        if len(runs) == 9:
            # Map data points strictly into the structured grid rows
            for idx, (lvl_name, rep_num, spike_amt, area, rec_pct) in enumerate(runs):
                self.table.setItem(idx, 2, QTableWidgetItem(str(spike_amt)))
                self.table.setItem(idx, 3, QTableWidgetItem(str(area)))
                
                rec_item = QTableWidgetItem(f"{rec_pct:.2f}%")
                rec_item.setFlags(rec_item.flags() & ~Qt.ItemIsEditable)
                rec_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(idx, 4, rec_item)

            self.calculate_accuracy_suite(silent=True)
        else:
            # No saved runs found, initialize clean slate
            self.initialize_empty_table()

    # ==========================================
    # MATHEMATICAL SOLVER & INTEGRATION
    # ==========================================
    def calculate_accuracy_suite(self, silent=False):
        """
        Uses active impurity linearity slope/intercept to resolve concentrations.
        If no linearity data exists, warns user to complete linearity study first!
        """
        if not self.active_imp:
            return

        # 1. Fetch active linearity parameters to translate peak area -> found concentration
        lin_runs = self.db.get_linearity_runs(self.active_imp["id"])
        if len(lin_runs) < 2:
            if not silent:
                QMessageBox.warning(
                    self, 
                    "Missing Linearity Curve", 
                    "Accuracy recovery calculations require an active impurity Linearity Curve to translate Peak Area to Concentration found!\n\nPlease complete and save the Linearity & RRF tab study first."
                )
            return

        # Solve active regression parameters
        imp_concs = [row[3] for row in lin_runs]
        imp_areas = [row[4] for row in lin_runs]
        reg_params = RelSubCalculator.calculate_regression(imp_concs, imp_areas)
        slope = reg_params["slope"]
        intercept = reg_params["intercept"]

        # 2. Iterate accuracy grid to compute individual % recoveries
        level_groups = {"LOQ": [], "100%": [], "150%": []}
        
        for row in range(9):
            try:
                lvl_name = self.table.item(row, 0).text()
                spiked_item = self.table.item(row, 2)
                area_item = self.table.item(row, 3)

                if spiked_item and area_item:
                    spiked = float(spiked_item.text())
                    area = float(area_item.text())

                    # Use linearity to get concentration found: x = (y - c)/m
                    conc_found = (area - intercept) / slope
                    recovery = (conc_found / spiked) * 100.0

                    level_groups[lvl_name].append(recovery)

                    # Update grid UI
                    rec_item = QTableWidgetItem(f"{recovery:.2f}%")
                    rec_item.setFlags(rec_item.flags() & ~Qt.ItemIsEditable)
                    rec_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 4, rec_item)
            except (AttributeError, ValueError):
                continue

        # 3. Compute stats for each level and update Summary layout labels
        for lvl, recoveries in level_groups.items():
            if len(recoveries) < 2:
                continue

            stats = RelSubCalculator.calculate_accuracy_stats(recoveries)
            mean_val = f"{stats['mean_recovery']:.2f}%"
            rsd_val = f"{stats['recovery_rsd']:.2f}%"

            if lvl == "LOQ":
                self.lbl_loq_mean.setText(f"Mean Recovery: {mean_val}")
                self.lbl_loq_rsd.setText(f"Recovery RSD: {rsd_val}")
            elif lvl == "100%":
                self.lbl_mid_mean.setText(f"Mean Recovery: {mean_val}")
                self.lbl_mid_rsd.setText(f"Recovery RSD: {rsd_val}")
            elif lvl == "150%":
                self.lbl_high_mean.setText(f"Mean Recovery: {mean_val}")
                self.lbl_high_rsd.setText(f"Recovery RSD: {rsd_val}")

        if not silent:
            QMessageBox.information(self, "Success", "Spiked Recovery recoveries and statistics solved successfully!")

    # ==========================================
    # DATA SAVING DIRECTLY IN SQLite
    # ==========================================
    def save_data_to_db(self):
        """Parses individual row recoveries and saves full matrix state in SQLite."""
        if not self.active_imp:
            return

        # Ensure we have active linearity parameters before saving
        lin_runs = self.db.get_linearity_runs(self.active_imp["id"])
        if len(lin_runs) < 2:
            QMessageBox.critical(self, "Data Error", "Cannot save accuracy records without an established linearity curve.")
            return

        raw_rows = []
        for row in range(9):
            try:
                lvl_name = self.table.item(row, 0).text()
                rep_num = int(self.table.item(row, 1).text())
                spiked = float(self.table.item(row, 2).text())
                area = float(self.table.item(row, 3).text())
                
                # Extract recovery float from the text percentage (e.g. "98.54%" -> 98.54)
                rec_text = self.table.item(row, 4).text().replace("%", "")
                recovery = float(rec_text) if rec_text != "-" else 0.0

                raw_rows.append((lvl_name, rep_num, spiked, area, recovery))
            except (AttributeError, ValueError):
                continue

        if len(raw_rows) < 9:
            QMessageBox.warning(self, "Validation Error", "Please fill in all 9 spiked accuracy replicate cells before saving.")
            return

        # Save to database
        self.db.save_accuracy_runs(self.active_imp["id"], raw_rows)
        QMessageBox.information(self, "Database Saved", "Spiked recovery records saved successfully!")