from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QLineEdit,
)
from PySide6.QtCore import Qt

class RecoveryLevelWidget(QFrame):
    def __init__(self, level_percentage, parent=None):
        super().__init__(parent)
        self.level_percentage = level_percentage
        self.replicates = 3
        
        # Input tracking lists
        self.spike_inputs = []  # Spike area inputs
        self.added_inputs = []  # Amount Added (mg) inputs
        
        # Calculated output tracking labels
        self.lbl_net_responses = []
        self.lbl_recovered_mgs = []
        self.lbl_pct_recoveries = []
        
        self.build_ui()

    def build_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                background-color: #FDFDFD;
                padding: 10px;
            }
            QLabel#levelTitle {
                font-size: 15px;
                font-weight: bold;
                color: #2C3E50;
            }
            QLabel#header {
                font-weight: bold;
                color: #34495E;
                border-bottom: 1px solid #E0E0E0;
                padding-bottom: 4px;
            }
            QLineEdit {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 4px;
                min-width: 90px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header Title
        title = QLabel(f"{self.level_percentage}% Spike Level Replicates")
        title.setObjectName("levelTitle")
        layout.addWidget(title)

        # Grid Layout for Replicates Table
        grid = QGridLayout()
        grid.setSpacing(10)

        # Table Column Headers
        headers = [
            "Replicate", 
            "Spike Response (Area)", 
            "Amount Added (mg)", 
            "Net Response", 
            "Recovered (mg)", 
            "Recovery (%)"
        ]
        for col, h_text in enumerate(headers):
            lbl = QLabel(h_text)
            lbl.setObjectName("header")
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, col)

        # Build Replicate Rows
        for i in range(self.replicates):
            # Row label
            lbl_rep = QLabel(f"Replicate {i+1}")
            lbl_rep.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl_rep, i + 1, 0)

            # 1. Spike Response (Area Input)
            txt_spike = QLineEdit()
            txt_spike.setPlaceholderText("0.00")
            txt_spike.setAlignment(Qt.AlignRight)
            grid.addWidget(txt_spike, i + 1, 1)
            self.spike_inputs.append(txt_spike)

            # 2. Amount Added (mg Input)
            txt_added = QLineEdit()
            txt_added.setPlaceholderText("0.00")
            txt_added.setAlignment(Qt.AlignRight)
            grid.addWidget(txt_added, i + 1, 2)
            self.added_inputs.append(txt_added)

            # 3. Net Response (Output Area)
            lbl_net = QLabel("0.00")
            lbl_net.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl_net, i + 1, 3)
            self.lbl_net_responses.append(lbl_net)

            # 4. Recovered Amount (Output mg)
            lbl_rec_mg = QLabel("0.0000")
            lbl_rec_mg.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl_rec_mg, i + 1, 4)
            self.lbl_recovered_mgs.append(lbl_rec_mg)

            # 5. Percent Recovery (Output %)
            lbl_pct = QLabel("0.00%")
            lbl_pct.setAlignment(Qt.AlignCenter)
            lbl_pct.setStyleSheet("font-weight: bold;")
            grid.addWidget(lbl_pct, i + 1, 5)
            self.lbl_pct_recoveries.append(lbl_pct)

        layout.addLayout(grid)

        # Level Summary Statistics Footer
        summary_frame = QFrame()
        summary_frame.setStyleSheet("border: none; background: transparent; padding: 0px;")
        summary_layout = QGridLayout(summary_frame)
        summary_layout.setContentsMargins(0, 5, 0, 0)
        summary_layout.setSpacing(15)

        self.lblMean = QLabel("0.00%")
        self.lblRSD = QLabel("0.00%")
        self.lblBias = QLabel("0.00%")
        self.lblStatus = QLabel("Pending")
        self.lblStatus.setStyleSheet("font-weight: bold; color: gray;")

        summary_layout.addWidget(QLabel("<b>Mean Recovery:</b>"), 0, 0)
        summary_layout.addWidget(self.lblMean, 0, 1)
        summary_layout.addWidget(QLabel("<b>% RSD:</b>"), 0, 2)
        summary_layout.addWidget(self.lblRSD, 0, 3)
        summary_layout.addWidget(QLabel("<b>% Bias:</b>"), 0, 4)
        summary_layout.addWidget(self.lblBias, 0, 5)
        summary_layout.addWidget(QLabel("<b>Status:</b>"), 0, 6)
        summary_layout.addWidget(self.lblStatus, 0, 7)

        layout.addWidget(summary_frame)

    # --- Helper methods to read/write clean values ---
    def spike_values(self):
        vals = []
        for inp in self.spike_inputs:
            try:
                vals.append(float(inp.text()) if inp.text().strip() else 0.0)
            except ValueError:
                vals.append(0.0)
        return vals

    def added_values(self):
        vals = []
        for inp in self.added_inputs:
            try:
                vals.append(float(inp.text()) if inp.text().strip() else 0.0)
            except ValueError:
                vals.append(0.0)
        return vals

    def set_replicate_outputs(self, row, net_response, recovered_mg, pct_recovery):
        self.lbl_net_responses[row].setText(f"{net_response:.2f}")
        self.lbl_recovered_mgs[row].setText(f"{recovered_mg:.4f}")
        self.lbl_pct_recoveries[row].setText(f"{pct_recovery:.2f}%")

    def set_summary(self, mean, rsd, bias, status):
        self.lblMean.setText(f"{mean:.2f}%")
        self.lblRSD.setText(f"{rsd:.2f}%")
        self.lblBias.setText(f"{bias:.2f}%")
        self.lblStatus.setText(status)
        if status == "PASS":
            self.lblStatus.setStyleSheet("color: green; font-weight: bold;")
        elif status == "FAIL":
            self.lblStatus.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.lblStatus.setStyleSheet("color: gray; font-weight: bold;")