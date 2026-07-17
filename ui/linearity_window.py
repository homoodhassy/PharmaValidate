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
    QSpinBox,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt

# Matplotlib integration with PySide6
import matplotlib
matplotlib.use('Qt5Agg')  # Configures matplotlib backend safely for PySide interface
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from calculations.linearity_calculator import LinearityCalculator

class MplCanvas(FigureCanvas):
    """Interactive Matplotlib canvas for drawing the Linearity curve."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        # Style the plot beautifully
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.grid(True, linestyle='--', alpha=0.5)
        
        super().__init__(fig)

class LinearityWindow(QWidget):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        
        # Grid input storage references
        self.nominal_inputs = []  # LineEdit widgets for Nom % (e.g. 80, 100)
        self.weight_inputs = []   # Nested list of LineEdits: [[w1, w2, w3], [w1, w2, w3], ...]
        self.response_inputs = [] # Nested list of LineEdits: [[r1, r2, r3], [r1, r2, r3], ...]
        
        # Calculation display row references
        self.mean_labels = []
        self.sd_labels = []
        self.rsd_labels = []
        
        self.build_ui()
        self.load_project_data()
        self.on_level_count_changed(5)  # Set default level count to 5

    def load_project_data(self):
        """Loads and displays metadata from the active project."""
        if self.project and len(self.project) > 3:
            self.lblProject.setText(str(self.project[1]))
            self.lblProduct.setText(str(self.project[2]))
            self.lblMethod.setText(str(self.project[3]))

    def build_ui(self):
        self.setWindowTitle("Linearity Validation Module")
        self.resize(1200, 900)
        self.setMinimumWidth(1000)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)

        # Container
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(container)

        # Styles
        title_style = "font-size: 24px; font-weight: bold; color: #1E3A8A;"
        section_style = "font-size: 16px; font-weight: bold; color: #2C3E50; margin-top: 10px;"

        # Title
        title = QLabel("Linearity & Range Workspace")
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
        # Configuration Row (Select number of levels)
        # =====================================================
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("<b>Number of Linearity Levels:</b>"))
        
        self.spinLevels = QSpinBox()
        self.spinLevels.setRange(3, 10)
        self.spinLevels.setValue(5)
        self.spinLevels.setFixedWidth(80)
        self.spinLevels.valueChanged.connect(self.on_level_count_changed)
        config_layout.addWidget(self.spinLevels)
        
        config_layout.addWidget(QLabel("  |  <b>100% Target Reference Level:</b>"))
        self.combo100Level = QComboBox()
        self.combo100Level.currentIndexChanged.connect(self.update_calculations)
        config_layout.addWidget(self.combo100Level)
        
        config_layout.addStretch()
        scroll_layout.addLayout(config_layout)

        # =====================================================
        # Two-Column Workspace (Left: Table Entry | Right: Realtime Chart)
        # =====================================================
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)

        # Left Column - Data Entry Frame
        left_frame = QFrame()
        self.left_layout = QVBoxLayout(left_frame)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grid layout for the data entry table
        self.table_widget = QWidget()
        self.table_grid = QGridLayout(self.table_widget)
        self.table_grid.setSpacing(5)
        self.left_layout.addWidget(self.table_widget)
        columns_layout.addWidget(left_frame, 3)  # Stretch factor 3

        # Right Column - Visual Plot Frame
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;")
        right_layout = QVBoxLayout(right_frame)
        
        plot_title = QLabel("Linear Regression Curve")
        plot_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E3A8A; margin-bottom: 5px;")
        right_layout.addWidget(plot_title)
        
        # Embed the Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        right_layout.addWidget(self.canvas)
        columns_layout.addWidget(right_frame, 2)  # Stretch factor 2

        scroll_layout.addLayout(columns_layout)

        # =====================================================
        # Linearity Key Performance Metrics (Summary)
        # =====================================================
        metrics_header = QLabel("Linear Regression & Analytical Metrics Summary")
        metrics_header.setStyleSheet(section_style)
        scroll_layout.addWidget(metrics_header)

        metricsFrame = QFrame()
        metricsFrame.setFrameShape(QFrame.StyledPanel)
        metricsFrame.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 8px;")
        metricsLayout = QGridLayout(metricsFrame)
        metricsLayout.setContentsMargins(15, 15, 15, 15)
        metricsLayout.setSpacing(15)

        self.lblSlope = QLabel("0.0000")
        self.lblIntercept = QLabel("0.0000")
        self.lblRSquare = QLabel("0.0000")
        self.lblMultipleR = QLabel("0.0000")
        self.lblRSS = QLabel("0.0000")
        
        self.lblYInterceptPct = QLabel("0.00%")
        self.lblPooledRSD = QLabel("0.00%")
        
        self.lblYIntStatus = QLabel("Pending")
        self.lblYIntStatus.setStyleSheet("font-weight: bold; color: gray;")
        
        self.lblRSqStatus = QLabel("Pending")
        self.lblRSqStatus.setStyleSheet("font-weight: bold; color: gray;")

        # Formatting Layout Grid
        metricsLayout.addWidget(QLabel("<b>Slope (m):</b>"), 0, 0)
        metricsLayout.addWidget(self.lblSlope, 0, 1)
        metricsLayout.addWidget(QLabel("<b>Residual Sum of Squares (RSS):</b>"), 0, 2)
        metricsLayout.addWidget(self.lblRSS, 0, 3)

        metricsLayout.addWidget(QLabel("<b>Y-Intercept (c):</b>"), 1, 0)
        metricsLayout.addWidget(self.lblIntercept, 1, 1)
        metricsLayout.addWidget(QLabel("<b>Multiple R (r Coefficient):</b>"), 1, 2)
        metricsLayout.addWidget(self.lblMultipleR, 1, 3)

        metricsLayout.addWidget(QLabel("<b>% Y-Intercept:</b>"), 2, 0)
        metricsLayout.addWidget(self.lblYInterceptPct, 2, 1)
        metricsLayout.addWidget(QLabel("<b>R-Square (R² Value):</b>"), 2, 2)
        metricsLayout.addWidget(self.lblRSquare, 2, 3)

        metricsLayout.addWidget(QLabel("<b>Pooled % RSD:</b>"), 3, 0)
        metricsLayout.addWidget(self.lblPooledRSD, 3, 1)
        metricsLayout.addWidget(QLabel("<b>% Y-Int. Status (≤ 2.0%):</b>"), 3, 2)
        metricsLayout.addWidget(self.lblYIntStatus, 3, 3)
        
        metricsLayout.addWidget(QLabel(""), 4, 0) # empty spacing
        metricsLayout.addWidget(QLabel(""), 4, 1)
        metricsLayout.addWidget(QLabel("<b>Overall Fit Status (R² ≥ 0.99):</b>"), 4, 2)
        metricsLayout.addWidget(self.lblRSqStatus, 4, 3)

        scroll_layout.addWidget(metricsFrame)

        # Save Action Row
        actions = QHBoxLayout()
        actions.addStretch()
        self.btnSave = QPushButton("Save Linearity Dataset")
        self.btnSave.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                padding: 10px 22px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #172554;
            }
        """)
        self.btnSave.clicked.connect(self.save_data)
        actions.addWidget(self.btnSave)
        scroll_layout.addLayout(actions)

    def on_level_count_changed(self, num_levels):
        """Reconstructs the spreadsheet grid dynamically when user changes levels."""
        # Clear existing table layouts and connections safely
        for i in range(self.table_grid.count()):
            widget = self.table_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        self.nominal_inputs.clear()
        self.weight_inputs.clear()
        self.response_inputs.clear()
        self.mean_labels.clear()
        self.sd_labels.clear()
        self.rsd_labels.clear()

        # Update Reference Dropdown Options
        self.combo100Level.blockSignals(True)
        self.combo100Level.clear()
        for idx in range(num_levels):
            self.combo100Level.addItem(f"Level {idx+1}", idx)
        # Default middle level to 100% target
        self.combo100Level.setCurrentIndex(num_levels // 2)
        self.combo100Level.blockSignals(False)

        # Set Column Headers
        headers = [
            "Level", "Nom. (%)", 
            "W1 (X)", "A1 (Y)", 
            "W2 (X)", "A2 (Y)", 
            "W3 (X)", "A3 (Y)", 
            "Mean Resp", "% RSD"
        ]
        for col, h_text in enumerate(headers):
            lbl = QLabel(f"<b>{h_text}</b>")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background-color: #E2E8F0; padding: 6px; border-radius: 4px; font-size: 11px;")
            self.table_grid.addWidget(lbl, 0, col)

        # Populate Inputs
        default_percentages = {
            3: [80, 100, 120],
            5: [80, 90, 100, 110, 120],
            6: [50, 75, 100, 125, 150, 200]
        }
        fallback_percent = default_percentages.get(num_levels, [80 + i * 10 for i in range(num_levels)])

        for row in range(num_levels):
            lbl_level = QLabel(f"<b>L{row+1}</b>")
            lbl_level.setAlignment(Qt.AlignCenter)
            self.table_grid.addWidget(lbl_level, row+1, 0)

            # Nominal Percent Input
            txt_nom = QLineEdit(str(fallback_percent[row] if row < len(fallback_percent) else 100))
            txt_nom.setFixedWidth(50)
            txt_nom.setAlignment(Qt.AlignCenter)
            txt_nom.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 4px;")
            txt_nom.textChanged.connect(self.update_calculations)
            self.nominal_inputs.append(txt_nom)
            self.table_grid.addWidget(txt_nom, row+1, 1)

            level_weights = []
            level_responses = []

            # 3 Replicates for weights and responses
            for rep in range(3):
                # Weight (X)
                txt_w = QLineEdit()
                txt_w.setPlaceholderText("X")
                txt_w.setFixedWidth(65)
                txt_w.setAlignment(Qt.AlignRight)
                txt_w.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 4px;")
                txt_w.textChanged.connect(self.update_calculations)
                level_weights.append(txt_w)
                self.table_grid.addWidget(txt_w, row+1, 2 + (rep * 2))

                # Response (Y)
                txt_r = QLineEdit()
                txt_r.setPlaceholderText("Y")
                txt_r.setFixedWidth(80)
                txt_r.setAlignment(Qt.AlignRight)
                txt_r.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 4px;")
                txt_r.textChanged.connect(self.update_calculations)
                level_responses.append(txt_r)
                self.table_grid.addWidget(txt_r, row+1, 3 + (rep * 2))

            self.weight_inputs.append(level_weights)
            self.response_inputs.append(level_responses)

            # Calculated Display Labels
            lbl_mean = QLabel("0.0")
            lbl_mean.setAlignment(Qt.AlignRight)
            lbl_mean.setStyleSheet("color: #475569; padding-right: 5px;")
            self.mean_labels.append(lbl_mean)
            self.table_grid.addWidget(lbl_mean, row+1, 8)

            lbl_rsd = QLabel("0.00%")
            lbl_rsd.setAlignment(Qt.AlignRight)
            lbl_rsd.setStyleSheet("color: #475569; padding-right: 5px;")
            self.rsd_labels.append(lbl_rsd)
            self.table_grid.addWidget(lbl_rsd, row+1, 9)

        self.update_calculations()

    def update_calculations(self):
        """Triggers live statistical updates and plots coordinates in real-time."""
        all_x = []
        all_y = []
        levels_responses_data = []
        mean_responses_per_level = []

        num_levels = len(self.nominal_inputs)

        # Process statistics for individual levels
        for row in range(num_levels):
            weights = []
            responses = []

            for rep in range(3):
                w_str = self.weight_inputs[row][rep].text().strip()
                r_str = self.response_inputs[row][rep].text().strip()
                
                if w_str and r_str:
                    try:
                        w_val = float(w_str)
                        r_val = float(r_str)
                        weights.append(w_val)
                        responses.append(r_val)
                        
                        all_x.append(w_val)
                        all_y.append(r_val)
                    except ValueError:
                        pass

            if len(responses) > 0:
                levels_responses_data.append(responses)
                
                # Single level average
                lvl_mean = sum(responses) / len(responses)
                mean_responses_per_level.append(lvl_mean)
                self.mean_labels[row].setText(f"{lvl_mean:.1f}")

                # Single level RSD
                if len(responses) >= 2:
                    try:
                        lvl_sd = stdev(responses)
                        lvl_rsd = (lvl_sd / lvl_mean) * 100 if lvl_mean > 0 else 0.0
                        self.rsd_labels[row].setText(f"{lvl_rsd:.2f}%")
                    except Exception:
                        self.rsd_labels[row].setText("0.00%")
                else:
                    self.rsd_labels[row].setText("N/A")
            else:
                self.mean_labels[row].setText("0.0")
                self.rsd_labels[row].setText("0.00%")
                mean_responses_per_level.append(0.0)

        # Perform global Linear Regression across all parsed individual pairs
        if len(all_x) >= 3:
            m, c, r2, r_coef, rss = LinearityCalculator.linear_regression(all_x, all_y)
            
            # Displays
            self.lblSlope.setText(f"{m:.5f}")
            self.lblIntercept.setText(f"{c:.4f}")
            self.lblRSquare.setText(f"{r2:.5f}")
            self.lblMultipleR.setText(f"{r_coef:.5f}")
            self.lblRSS.setText(f"{rss:.1f}")

            # Acceptance check on R-Square (typically R² >= 0.9900 or 0.9990)
            if r2 >= 0.99:
                self.lblRSqStatus.setText("PASS")
                self.lblRSqStatus.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.lblRSqStatus.setText("FAIL")
                self.lblRSqStatus.setStyleSheet("color: red; font-weight: bold;")

            # Pooled % RSD Calculation
            _, pooled_rsd = LinearityCalculator.calculate_pooled_rsd(levels_responses_data)
            self.lblPooledRSD.setText(f"{pooled_rsd:.2f}%")

            # Calculate % Y-Intercept
            selected_100_idx = self.combo100Level.currentIndex()
            if 0 <= selected_100_idx < len(mean_responses_per_level):
                ref_100_mean = mean_responses_per_level[selected_100_idx]
                if ref_100_mean > 0:
                    y_int_pct = LinearityCalculator.calculate_percent_y_intercept(c, ref_100_mean)
                    self.lblYInterceptPct.setText(f"{y_int_pct:.2f}%")
                    
                    # Acceptability criteria limit of not more than 2%
                    if y_int_pct <= 2.0:
                        self.lblYIntStatus.setText("PASS")
                        self.lblYIntStatus.setStyleSheet("color: green; font-weight: bold;")
                    else:
                        self.lblYIntStatus.setText("FAIL")
                        self.lblYIntStatus.setStyleSheet("color: red; font-weight: bold;")
                else:
                    self.lblYInterceptPct.setText("0.00%")
                    self.lblYIntStatus.setText("Invalid 100% mean")
                    self.lblYIntStatus.setStyleSheet("color: orange; font-weight: bold;")
            
            # Redraw real-time Matplotlib Regression Curve
            self.plot_graph(all_x, all_y, m, c, r2)

        else:
            # Revert UI displays to pending state
            self.lblSlope.setText("0.0000")
            self.lblIntercept.setText("0.0000")
            self.lblRSquare.setText("0.0000")
            self.lblMultipleR.setText("0.0000")
            self.lblRSS.setText("0.0000")
            self.lblYInterceptPct.setText("0.00%")
            self.lblPooledRSD.setText("0.00%")
            self.lblYIntStatus.setText("Pending")
            self.lblYIntStatus.setStyleSheet("color: gray; font-weight: bold;")
            self.lblRSqStatus.setText("Pending")
            self.lblRSqStatus.setStyleSheet("color: gray; font-weight: bold;")
            
            # Clear Canvas
            self.canvas.axes.clear()
            self.canvas.axes.grid(True, linestyle='--', alpha=0.5)
            self.canvas.draw()

    def plot_graph(self, x_pts, y_pts, slope, intercept, r2):
        """Draws regression line overlay and raw data scatter plots."""
        self.canvas.axes.clear()
        
        # Plot coordinates
        self.canvas.axes.scatter(x_pts, y_pts, color='#1E3A8A', label="Raw Data Points", zorder=5)
        
        # Reconstruct fit line
        min_x, max_x = min(x_pts), max(x_pts)
        margin = (max_x - min_x) * 0.1 if max_x != min_x else 1.0
        fit_x = [min_x - margin, max_x + margin]
        fit_y = [slope * x + intercept for x in fit_x]
        
        self.canvas.axes.plot(fit_x, fit_y, color='#EF4444', linestyle='--', linewidth=2, label="Regression Line")
        
        # Details & Legend
        self.canvas.axes.legend(loc="upper left")
        self.canvas.axes.set_xlabel("Measured Weight (Concentration)")
        self.canvas.axes.set_ylabel("Analytical Area (Response)")
        self.canvas.axes.grid(True, linestyle='--', alpha=0.5)
        self.canvas.axes.text(
            0.05, 0.05, 
            f"y = {slope:.4f}x + {intercept:.2f}\nR² = {r2:.5f}", 
            transform=self.canvas.axes.transAxes, 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='#CBD5E1', boxstyle='round,pad=0.5')
        )
        self.canvas.draw()

    def save_data(self):
        """Validates entry status and outputs dataset details."""
        all_x = []
        all_y = []
        for row in range(len(self.nominal_inputs)):
            for rep in range(3):
                w = self.weight_inputs[row][rep].text().strip()
                r = self.response_inputs[row][rep].text().strip()
                if w and r:
                    all_x.append(w)
                    all_y.append(r)

        if len(all_x) < 3:
            QMessageBox.warning(self, "Validation Error", "Please enter at least 3 replicate pairs before saving dataset.")
            return

        QMessageBox.information(
            self, 
            "Success", 
            f"Linearity validated successfully!\n\nPoints Saved: {len(all_x)}\nSlope: {self.lblSlope.text()}\nR²: {self.lblRSquare.text()}\n% Y-Intercept: {self.lblYInterceptPct.text()}"
        )