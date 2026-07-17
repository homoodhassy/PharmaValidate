"""
PharmaValidate v0.5 - Specificity & Forced Degradation Sub-module
Provides interactive calculators for Resolution (Rs) of critical peak pairs
and a stress testing ledger for forced degradation studies.
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
    QComboBox,
    QCheckBox,
)
from PySide6.QtCore import Qt

class RelSubSpecificityWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_imp = None
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Module Header
        self.lbl_title = QLabel("🛡️ Specificity & Forced Degradation Study")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        main_layout.addWidget(self.lbl_title)

        # Split Layout: Top (Critical Resolution) | Bottom (Forced Degradation)
        # ==========================================
        # SECTION 1: CRITICAL PEAK RESOLUTION (Rs)
        # ==========================================
        res_container = QFrame()
        res_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        res_layout = QVBoxLayout(res_container)
        res_layout.setContentsMargins(12, 12, 12, 12)
        res_layout.setSpacing(10)

        res_layout.addWidget(QLabel("<b>Part A: Critical Separation Resolution ($R_s$)</b>"))
        res_layout.addWidget(QLabel("<small style='color:#64748B;'>Enter peak retention times ($t_R$) and tangent widths ($W$) to evaluate critical pair resolution.</small>"))

        self.table_res = QTableWidget(2, 5)
        self.table_res.setHorizontalHeaderLabels([
            "Peak Identity", 
            "Retention Time\n(tR, min)", 
            "Peak Width\n(W, min)", 
            "Calculated Resolution\n(Rs)",
            "System Suitability\nStatus"
        ])
        self.table_res.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_res.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #E2E8F0; border: 1px solid #E2E8F0; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; border: 1px solid #E2E8F0; }
        """)
        
        self.initialize_resolution_table()
        res_layout.addWidget(self.table_res)

        # Resolution Action Layout
        res_action_layout = QHBoxLayout()
        self.btn_calculate_res = QPushButton("Calculate Critical Resolution")
        self.btn_calculate_res.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 6px 15px; border-radius: 4px; border:none;")
        self.btn_calculate_res.clicked.connect(self.calculate_resolution)
        res_action_layout.addWidget(self.btn_calculate_res)
        res_action_layout.addStretch()
        res_layout.addLayout(res_action_layout)

        main_layout.addWidget(res_container)

        # ==========================================
        # SECTION 2: FORCED DEGRADATION MATRIX
        # ==========================================
        deg_container = QFrame()
        deg_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        deg_layout = QVBoxLayout(deg_container)
        deg_layout.setContentsMargins(12, 12, 12, 12)
        deg_layout.setSpacing(10)

        deg_layout.addWidget(QLabel("<b>Part B: Forced Degradation (Stress Stability) Matrix</b>"))
        deg_layout.addWidget(QLabel("<small style='color:#64748B;'>Input Active Substance peak areas to determine degradation recovery and monitor peak purity.</small>"))

        # Predefined stress conditions under ICH guidelines
        self.table_deg = QTableWidget(5, 6)
        self.table_deg.setHorizontalHeaderLabels([
            "Stress Condition", 
            "Control Area\n(counts)", 
            "Stressed Area\n(counts)", 
            "Degradation\n(%)",
            "Peak Purity\n(Angle < Threshold)",
            "Interference Checked?"
        ])
        self.table_deg.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_deg.setStyleSheet("""
            QTableWidget { background-color: white; gridline-color: #E2E8F0; border: 1px solid #E2E8F0; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; border: 1px solid #E2E8F0; }
        """)
        
        self.initialize_degradation_table()
        deg_layout.addWidget(self.table_deg)

        # Degradation Actions
        deg_action_layout = QHBoxLayout()
        self.btn_calculate_deg = QPushButton("Calculate Stress Recovery")
        self.btn_calculate_deg.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 6px 15px; border-radius: 4px; border:none;")
        self.btn_calculate_deg.clicked.connect(self.calculate_degradation)
        deg_action_layout.addWidget(self.btn_calculate_deg)
        deg_action_layout.addStretch()
        deg_layout.addLayout(deg_action_layout)

        main_layout.addWidget(deg_container)

    # ==========================================
    # INITIALIZATION & SETUP
    # ==========================================
    def initialize_resolution_table(self):
        # Peak 1 (e.g. Active Ingredient)
        item_pk1 = QTableWidgetItem("Active Drug Substance")
        self.table_res.setItem(0, 0, item_pk1)
        
        # Peak 2 (The closest eluting impurity)
        item_pk2 = QTableWidgetItem("Nearest Impurity")
        self.table_res.setItem(1, 0, item_pk2)

        # Set calculated columns to read-only
        for row in range(2):
            for col in [3, 4]:
                item = QTableWidgetItem("-")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_res.setItem(row, col, item)

    def initialize_degradation_table(self):
        conditions = [
            "Acid Stress (0.1 M HCl, Heat)", 
            "Base Stress (0.1 M NaOH, Heat)", 
            "Oxidative (3% H2O2)", 
            "Thermal Stress (60°C dry)", 
            "Photolytic Stress (UV/Vis)"
        ]

        for row, condition in enumerate(conditions):
            cond_item = QTableWidgetItem(condition)
            cond_item.setFlags(cond_item.flags() & ~Qt.ItemIsEditable)
            self.table_deg.setItem(row, 0, cond_item)

            # Calculated Degradation percentage
            deg_item = QTableWidgetItem("-")
            deg_item.setFlags(deg_item.flags() & ~Qt.ItemIsEditable)
            deg_item.setTextAlignment(Qt.AlignCenter)
            self.table_deg.setItem(row, 3, deg_item)

            # Dropdown for Peak Purity status
            combo_purity = QComboBox()
            combo_purity.addItems(["Purity Passes", "Purity Fails", "Not Evaluated"])
            self.table_deg.setCellWidget(row, 4, combo_purity)

            # --- BUG FIX: Create & center a real QCheckBox widget inside the cell ---
            container_widget = QWidget()
            layout = QHBoxLayout(container_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            
            chk = QCheckBox()
            chk.setChecked(True)  # Default to checked/safe state
            chk.setStyleSheet("margin: 0px; padding: 0px;")
            
            layout.addWidget(chk)
            self.table_deg.setCellWidget(row, 5, container_widget)

    # ==========================================
    # MATHEMATICAL COMPUTATIONS
    # ==========================================
    def calculate_resolution(self):
        """Computes chromatographic resolution using the USP tangent formula."""
        try:
            tr1_item = self.table_res.item(0, 1)
            w1_item = self.table_res.item(0, 2)
            tr2_item = self.table_res.item(1, 1)
            w2_item = self.table_res.item(1, 2)

            if not (tr1_item and w1_item and tr2_item and w2_item):
                QMessageBox.warning(self, "Data Error", "Please fill in Retention Times and Peak Widths for both compounds.")
                return

            tr1, w1 = float(tr1_item.text()), float(w1_item.text())
            tr2, w2 = float(tr2_item.text()), float(w2_item.text())

            if w1 + w2 <= 0:
                raise ValueError("Peak widths must be greater than zero.")

            # Ensure we calculate the positive difference
            resolution = (2.0 * abs(tr2 - tr1)) / (w1 + w2)

            # Update results in row 1
            res_item = QTableWidgetItem(f"{resolution:.2f}")
            res_item.setFlags(res_item.flags() & ~Qt.ItemIsEditable)
            res_item.setTextAlignment(Qt.AlignCenter)
            self.table_res.setItem(1, 3, res_item)

            # System Suitability assessment (Standard pharmaceutical threshold is >= 1.5)
            status = "Acceptable (Rs ≥ 1.5)" if resolution >= 1.5 else "Inadequate (Rs < 1.5)"
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            if resolution >= 1.5:
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.red)
                
            self.table_res.setItem(1, 4, status_item)

        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Failed to calculate Resolution: {str(e)}")

    def calculate_degradation(self):
        """Calculates percent degradation based on control vs stressed Peak Area."""
        calculations_made = False
        
        for row in range(5):
            try:
                control_item = self.table_deg.item(row, 1)
                stressed_item = self.table_deg.item(row, 2)

                if control_item and stressed_item:
                    control_area = float(control_item.text())
                    stressed_area = float(stressed_item.text())

                    if control_area <= 0:
                        continue

                    # % Degradation formula
                    pct_deg = ((control_area - stressed_area) / control_area) * 100.0

                    deg_item = QTableWidgetItem(f"{pct_deg:.2f}%")
                    deg_item.setFlags(deg_item.flags() & ~Qt.ItemIsEditable)
                    deg_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Highlight typical target forced-degradation sweet spot (5% to 20%)
                    if 5.0 <= pct_deg <= 20.0:
                        deg_item.setForeground(Qt.darkGreen)
                    else:
                        deg_item.setForeground(Qt.blue)

                    self.table_deg.setItem(row, 3, deg_item)
                    calculations_made = True
            except ValueError:
                continue

        if calculations_made:
            QMessageBox.information(self, "Success", "Forced degradation profiles calculated successfully.")
        else:
            QMessageBox.warning(self, "Input Error", "No complete Control/Stressed area pairs were found to compute degradation.")

    # ==========================================
    # WORKSPACE COMPATIBILITY LOADERS
    # ==========================================
    def set_active_impurity(self, profile):
        """Updates internal target when active impurity shifts in the workspace."""
        self.active_imp = profile
        if not profile:
            self.lbl_title.setText("🛡️ Specificity & Forced Degradation Study")
            self.setEnabled(False)
            return

        self.setEnabled(True)
        self.lbl_title.setText(f"🛡️ Specificity Evaluation for: {profile['name']}")
        
        # Automatically insert the current active impurity name into Peak 2
        imp_name_item = QTableWidgetItem(profile['name'])
        self.table_res.setItem(1, 0, imp_name_item)