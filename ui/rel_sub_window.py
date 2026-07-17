"""
PharmaValidate v0.5 - Related Substances Integrated Dashboard
Manages the validation lifecycle of chromatographic impurities under ICH Q2 guidelines.
Fully integrated with Linearity/RRF, LOD/LOQ, and Spiked Recovery sub-modules.
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
    QComboBox,
    QCheckBox,
    QScrollArea,
    QMessageBox,
    QTabWidget,
)
from PySide6.QtCore import Qt

# Import our backend components
from database.rel_sub_db import RelSubDatabase
from calculations.rel_sub_calculator import RelSubCalculator

# Import our fully developed sub-tab modules
from ui.rel_sub_linearity import RelSubLinearityWidget
from ui.rel_sub_lod_loq import RelSubLodLoqWidget
from ui.rel_sub_accuracy import RelSubAccuracyWidget
from ui.rel_sub_specificity import RelSubSpecificityWidget

class RelSubWindow(QWidget):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        
        # Resolve Project Metadata
        # Expected tuple: (id, name, product, method, ...)
        self.project_id = self.project[0] if self.project else 1
        
        # Initialize Database
        self.db = RelSubDatabase()
        
        # Active Impurity Tracking
        self.active_impurity_id = None
        self.impurity_list = []

        self.build_ui()
        self.load_project_metadata()
        self.refresh_impurity_dropdown()

    def load_project_metadata(self):
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))
        else:
            self.lblProject.setText("Standalone Validation Study")
            self.lblProduct.setText("Active Pharmaceutical Ingredient")
            self.lblMethod.setText("RP-HPLC Impurities Method")

    def build_ui(self):
        self.setWindowTitle("Related Substances (Impurities) Validation Module")
        self.resize(1180, 850)
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
        title = QLabel("Related Substances Validation Workspace")
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

        # ==================================================================
        # IMPURITY CONFIGURATION REGISTRY PANEL
        # ==================================================================
        config_frame = QFrame()
        config_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(15, 15, 15, 15)
        config_layout.setSpacing(12)

        config_title = QLabel("Impurity Identification & Specifications")
        config_title.setStyleSheet("font-size:16px; font-weight:bold; color:#1E3A8A; border-bottom:2px solid #3B82F6; padding-bottom:5px;")
        config_layout.addWidget(config_title)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(15)

        # Impurity selector dropdown
        dropdown_vbox = QVBoxLayout()
        dropdown_vbox.addWidget(QLabel("<b>Active Impurity:</b>"))
        self.combo_impurities = QComboBox()
        self.combo_impurities.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px; min-width: 180px;")
        self.combo_impurities.currentIndexChanged.connect(self.on_impurity_changed)
        dropdown_vbox.addWidget(self.combo_impurities)
        inputs_layout.addLayout(dropdown_vbox)

        # Impurity Name input
        name_vbox = QVBoxLayout()
        name_vbox.addWidget(QLabel("<b>Impurity Name:</b>"))
        self.txt_imp_name = QLineEdit()
        self.txt_imp_name.setPlaceholderText("e.g. Impurity A / Salicylic Acid")
        self.txt_imp_name.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        name_vbox.addWidget(self.txt_imp_name)
        inputs_layout.addLayout(name_vbox)

        # Spec limit input
        limit_vbox = QVBoxLayout()
        limit_vbox.addWidget(QLabel("<b>Specification Limit (%):</b>"))
        self.txt_spec_limit = QLineEdit("0.15")
        self.txt_spec_limit.setPlaceholderText("0.15")
        self.txt_spec_limit.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        limit_vbox.addWidget(self.txt_spec_limit)
        inputs_layout.addLayout(limit_vbox)

        # RRF Configs
        rrf_vbox = QVBoxLayout()
        rrf_vbox.addWidget(QLabel("<b>Apply RRF Correction?</b>"))
        self.chk_use_rrf = QCheckBox("Use RRF")
        self.chk_use_rrf.stateChanged.connect(self.on_rrf_toggled)
        rrf_vbox.addWidget(self.chk_use_rrf)
        inputs_layout.addLayout(rrf_vbox)

        self.rrf_input_vbox = QVBoxLayout()
        self.rrf_input_vbox.addWidget(QLabel("<b>RRF Value:</b>"))
        self.txt_rrf_val = QLineEdit("1.0")
        self.txt_rrf_val.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px;")
        self.rrf_input_vbox.addWidget(self.txt_rrf_val)
        inputs_layout.addLayout(self.rrf_input_vbox)

        config_layout.addLayout(inputs_layout)

        # Registry Action Buttons
        buttons_layout = QHBoxLayout()
        
        btn_add = QPushButton("+ Register New Impurity")
        btn_add.setStyleSheet("background-color: #3B82F6; color: white; font-weight: bold; padding: 7px 15px; border-radius: 5px; border:none;")
        btn_add.clicked.connect(self.add_new_impurity)
        buttons_layout.addWidget(btn_add)

        btn_save_config = QPushButton("Save Current Profile")
        btn_save_config.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 7px 15px; border-radius: 5px; border:none;")
        btn_save_config.clicked.connect(self.save_impurity_config)
        buttons_layout.addWidget(btn_save_config)

        btn_delete = QPushButton("Delete Impurity Profile")
        btn_delete.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 7px 15px; border-radius: 5px; border:none;")
        btn_delete.clicked.connect(self.delete_impurity)
        buttons_layout.addWidget(btn_delete)

        buttons_layout.addStretch()
        config_layout.addLayout(buttons_layout)

        scroll_layout.addWidget(config_frame)

        # ==================================================================
        # TAB CONTAINER FOR SUB-MODULES
        # ==================================================================
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; border-radius: 8px; background: white; }
            QTabBar::tab { background: #F1F5F9; color: #475569; padding: 10px 20px; font-weight: bold; border: 1px solid #E2E8F0; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: white; color: #1E3A8A; border-bottom: 2px solid #1E3A8A; }
        """)

        # Initialize real, validated sub-modules
        self.tab_linearity = RelSubLinearityWidget(self)
        self.tab_lod_loq = RelSubLodLoqWidget(self)
        self.tab_accuracy = RelSubAccuracyWidget(self)
        self.tab_specificity = RelSubSpecificityWidget(self)

        self.tab_widget.addTab(self.tab_linearity, "Linearity & Relative Response Factors (RRF)")
        self.tab_widget.addTab(self.tab_lod_loq, "Sensitivity Limit (LOD & LOQ)")
        self.tab_widget.addTab(self.tab_accuracy, "Spiked Recovery (Accuracy)")
        self.tab_widget.addTab(self.tab_specificity, "Specificity (Separation & Degradation)")

        scroll_layout.addWidget(self.tab_widget)

    # ==========================================
    # WORKSPACE EVENTS & LOGIC
    # ==========================================
    def on_rrf_toggled(self, state):
        """Enables/disables RRF input box dynamically based on checkbox."""
        self.txt_rrf_val.setEnabled(state == Qt.Checked)

    def refresh_impurity_dropdown(self, select_impurity_id=None):
        """Loads registered impurities from SQLite into the dropdown selector."""
        self.combo_impurities.blockSignals(True)
        self.combo_impurities.clear()
        
        self.impurity_list = self.db.get_impurities_by_project(self.project_id)
        
        for imp in self.impurity_list:
            display_text = f"{imp['name']} (Spec: {imp['spec_limit']}%)"
            self.combo_impurities.addItem(display_text, imp["id"])
            
        self.combo_impurities.blockSignals(False)

        if len(self.impurity_list) > 0:
            # Re-select specified index or default to first
            target_idx = 0
            if select_impurity_id:
                for idx, imp in enumerate(self.impurity_list):
                    if imp["id"] == select_impurity_id:
                        target_idx = idx
                        break
            self.combo_impurities.setCurrentIndex(target_idx)
            self.on_impurity_changed(target_idx)
        else:
            self.active_impurity_id = None
            self.txt_imp_name.clear()
            self.txt_spec_limit.setText("0.15")
            self.chk_use_rrf.setChecked(False)
            self.txt_rrf_val.setText("1.0")
            self.propagate_impurity_selection(None)

    def on_impurity_changed(self, index):
        """Triggers when the user selects a different impurity from the dropdown."""
        if index < 0 or index >= len(self.impurity_list):
            return
            
        imp = self.impurity_list[index]
        self.active_impurity_id = imp["id"]
        
        # Populate UI Configuration
        self.txt_imp_name.setText(imp["name"])
        self.txt_spec_limit.setText(str(imp["spec_limit"]))
        self.chk_use_rrf.setChecked(imp["use_rrf"])
        self.txt_rrf_val.setText(str(imp["rrf_value"]))
        self.txt_rrf_val.setEnabled(imp["use_rrf"])

        # Update and cascade state to sub-tabs
        self.propagate_impurity_selection(imp)

    def propagate_impurity_selection(self, impurity_profile):
        """Informs child widgets to reload validation datasets for the newly chosen impurity."""
        self.tab_linearity.set_active_impurity(impurity_profile)
        self.tab_lod_loq.set_active_impurity(impurity_profile)
        self.tab_accuracy.set_active_impurity(impurity_profile)
        self.tab_specificity.set_active_impurity(impurity_profile)

    # ==========================================
    # REGISTRY DATABASE MUTATIONS
    # ==========================================
    def add_new_impurity(self):
        """Creates an empty template impurity profile in the database."""
        default_name = f"New Impurity {len(self.impurity_list) + 1}"
        new_id = self.db.add_impurity(
            project_id=self.project_id,
            name=default_name,
            spec_limit=0.15,
            use_rrf=False,
            rrf_value=1.0
        )
        self.refresh_impurity_dropdown(select_impurity_id=new_id)

    def save_impurity_config(self):
        """Saves adjustments made to the selected impurity profile properties."""
        if not self.active_impurity_id:
            QMessageBox.warning(self, "Validation Warning", "No active impurity profile selected to update.")
            return

        name = self.txt_imp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Warning", "Impurity Name cannot be empty.")
            return

        try:
            limit = float(self.txt_spec_limit.text())
            rrf_val = float(self.txt_rrf_val.text()) if self.chk_use_rrf.isChecked() else 1.0
        except ValueError:
            QMessageBox.critical(self, "Validation Error", "Please ensure Limit and RRF are numeric values.")
            return

        # Commit updates to metadata table
        self.db.update_impurity_config(self.active_impurity_id, limit, self.chk_use_rrf.isChecked(), rrf_val)
        
        # Perform custom query rename on database connection
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE rel_sub_impurities SET impurity_name = ? WHERE id = ?", (name, self.active_impurity_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", f"Impurity '{name}' successfully updated!")
        self.refresh_impurity_dropdown(select_impurity_id=self.active_impurity_id)

    def delete_impurity(self):
        """Removes an impurity along with its entire cascaded validation records."""
        if not self.active_impurity_id:
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this impurity? This will permanently erase ALL associated Linearity, LOD/LOQ, and Spiked Recovery raw runs!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_impurity(self.active_impurity_id)
            self.refresh_impurity_dropdown()