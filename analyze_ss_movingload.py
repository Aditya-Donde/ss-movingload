import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt

###############################################
# Analysis Functions 
###############################################

def analyze_beam(L, W1, W2, x):
    """
    Compute static analysis outputs for a simply supported beam with two moving loads.
    Loads are assumed to be applied at positions 0 (W1) and x (W2).
    Returns a dictionary with:
      - R_A: Reaction at Support A (kN)
      - R_B: Reaction at Support B (kN)
      - BM_01: Bending moment at x=0 (kN·m)
      - SF_01: Shear force at mid-span (kN)
      - SF_max: Maximum shear force (kN)
      - SF_max_loc: Location of maximum shear force (m from A)
      - BM_max: Maximum bending moment (kN·m)
      - BM_max_loc: Location of maximum bending moment (m from A)
    """
    R_B = (W2 * x) / L
    R_A = W1 + W2 - R_B
    BM_01 = 0  # At the support of a simply supported beam
    mid_span = 0.5 * L
    if mid_span < x:
        SF_01 = R_A - W1
    else:
        SF_01 = R_A - (W1 + W2)
    
    num_positions = 200
    num_sections = 200
    p1_positions = np.linspace(0, L - x, num=num_positions)
    y_positions = np.linspace(0, L, num=num_sections)
    
    max_shear = -np.inf
    max_shear_loc = None
    max_moment = -np.inf
    max_moment_loc = None
    
    for p1 in p1_positions:
        p2 = p1 + x
        RA_config = W1 * (L - p1) / L + W2 * (L - p2) / L
        for y in y_positions:
            shear = RA_config
            if y >= p1:
                shear -= W1
            if y >= p2:
                shear -= W2
            moment = RA_config * y
            if y >= p1:
                moment -= W1 * (y - p1)
            if y >= p2:
                moment -= W2 * (y - p2)
            if shear > max_shear:
                max_shear = shear
                max_shear_loc = y
            if moment > max_moment:
                max_moment = moment
                max_moment_loc = y
                
    return {
        'R_A': R_A,
        'R_B': R_B,
        'BM_01': BM_01,
        'SF_01': SF_01,
        'SF_max': max_shear,
        'SF_max_loc': max_shear_loc,
        'BM_max': max_moment,
        'BM_max_loc': max_moment_loc
    }

def calculate_BM_SF(L, W1, W2, p1, x, y_positions):
    """
    Calculate the bending moment (BM) and shear force (SF) distribution along the beam.
    
    Parameters:
        L          : Beam length (m)
        W1, W2     : Load values (kN)
        p1         : Position of first load (m)
        x          : Distance between loads (m) so that p2 = p1 + x
        y_positions: Array of positions along the beam (m)
        
    Returns:
        BM, SF: Arrays containing the bending moment (kN·m) and shear force (kN) values.
    """
    p2 = p1 + x
    RA = W1 * (L - p1) / L + W2 * (L - p2) / L
    BM = np.zeros_like(y_positions)
    SF = np.zeros_like(y_positions)
    
    for i, y in enumerate(y_positions):
        shear = RA
        if y >= p1:
            shear -= W1
        if y >= p2:
            shear -= W2
        SF[i] = shear
        
        moment = RA * y
        if y >= p1:
            moment -= W1 * (y - p1)
        if y >= p2:
            moment -= W2 * (y - p2)
        BM[i] = moment
    
    return BM, SF

###############################################
# GUI with PyQt and Matplotlib Animation
###############################################

class MplCanvas(FigureCanvas):
    """Matplotlib Canvas widget for embedding plots in PyQt."""
    def __init__(self, parent=None, width=5, height=8, dpi=100):
        # Create figure with two subplots and adjust vertical spacing.
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(width, height), dpi=dpi)
        self.fig.subplots_adjust(hspace=0.5)
        super().__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Analysis GUI")
        self.setGeometry(100, 100, 1000, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Left side: Animated plot
        self.canvas = MplCanvas(self, width=5, height=8, dpi=100)
        main_layout.addWidget(self.canvas, 2)
        
        # Right side: Input and Output
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 1)
        
        # Input Section
        input_group = QGroupBox("Input Parameters")
        input_layout = QFormLayout()
        input_group.setLayout(input_layout)
        
        self.le_length = QLineEdit("10")
        self.le_load1  = QLineEdit("20")
        self.le_load2  = QLineEdit("30")
        self.le_distance = QLineEdit("4")
        
        input_layout.addRow("Beam Length (m):", self.le_length)
        input_layout.addRow("Load 1 (kN):", self.le_load1)
        input_layout.addRow("Load 2 (kN):", self.le_load2)
        input_layout.addRow("Distance between loads (m):", self.le_distance)
        right_layout.addWidget(input_group)
        
        # Button for update
        self.btn_update = QPushButton("Update Analysis")
        self.btn_update.clicked.connect(self.update_analysis)
        right_layout.addWidget(self.btn_update)
        
        # Output Section
        output_group = QGroupBox("Output Results")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        self.lbl_output = QLabel("")
        self.lbl_output.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        output_layout.addWidget(self.lbl_output)
        right_layout.addWidget(output_group)
        
        # Animation parameters
        self.num_frames = 100
        self.num_sections = 300
        self.animation = None
        self.animation_started = False  # Animation will start after update
        
    def update_analysis(self):
        """Update outputs and start animation based on user inputs."""
        try:
            L = float(self.le_length.text())
            W1 = float(self.le_load1.text())
            W2 = float(self.le_load2.text())
            x  = float(self.le_distance.text())
            if x > L:
                self.lbl_output.setText("Error: Distance between loads cannot exceed beam length.")
                return
            
            # Compute static outputs via analyze_beam
            results = analyze_beam(L, W1, W2, x)
            output_text = (
                f"Reaction at A: {results['R_A']:.2f} kN\n"
                f"Reaction at B: {results['R_B']:.2f} kN\n"
                f"Bending Moment at x=0 (BM_01): {results['BM_01']:.2f} kN·m\n"
                f"Shear Force at mid-span (SF_01): {results['SF_01']:.2f} kN\n"
                f"Maximum Shear Force (SF_max): {results['SF_max']:.2f} kN at {results['SF_max_loc']:.2f} m\n"
                f"Maximum Bending Moment (BM_max): {results['BM_max']:.2f} kN·m at {results['BM_max_loc']:.2f} m"
            )
            self.lbl_output.setText(output_text)
            
            # Start animation after update
            self.init_animation()
            self.animation_started = True
        except Exception as e:
            self.lbl_output.setText("Error: " + str(e))
    
    def init_animation(self):
        """Set up and start the animation with current input parameters."""
        # Stop any existing animation
        if self.animation:
            self.animation.event_source.stop()
        
        try:
            L = float(self.le_length.text())
            W1 = float(self.le_load1.text())
            W2 = float(self.le_load2.text())
            x  = float(self.le_distance.text())
        except Exception:
            return
        
        # Prepare beam sections and load positions for animation
        y_positions = np.linspace(0, L, self.num_sections)
        p1_positions = np.linspace(0, L - x, self.num_frames)
        
        # Clear axes and configure
        self.canvas.ax1.clear()
        self.canvas.ax2.clear()
        self.canvas.ax1.set_xlim(0, L)
        self.canvas.ax2.set_xlim(0, L)
        self.canvas.ax1.set_title("Bending Moment Distribution")
        self.canvas.ax1.set_xlabel("Beam Length (m)")
        self.canvas.ax1.set_ylabel("Bending Moment (kN·m)")
        self.canvas.ax2.set_title("Shear Force Distribution")
        self.canvas.ax2.set_xlabel("Beam Length (m)")
        self.canvas.ax2.set_ylabel("Shear Force (kN)")
        
        # Draw vertical reference line at x=0 on both plots
        self.canvas.ax1.axhline(y=0, color='gray', linestyle='--')
        self.canvas.ax2.axhline(y=0, color='gray', linestyle='--')
        
        # Set heuristic y-limits
        self.canvas.ax1.set_ylim(-max(W1, W2)*L, max(W1, W2)*L)
        self.canvas.ax2.set_ylim(-max(W1, W2)*2, max(W1, W2)*2)
        
        # Initialize plot lines and annotation text
        self.line_bm, = self.canvas.ax1.plot([], [], 'b-', lw=2, label="BM")
        self.line_sf, = self.canvas.ax2.plot([], [], 'r-', lw=2, label="SF")
        self.text_pos = self.canvas.ax1.text(0.05, 0.9, '', transform=self.canvas.ax1.transAxes, fontsize=10)
        
        def update(frame):
            # For each frame, compute current load position and update BM, SF
            p1 = p1_positions[frame]
            p2 = p1 + x
            BM, SF = calculate_BM_SF(L, W1, W2, p1, x, y_positions)
            self.line_bm.set_data(y_positions, BM)
            self.line_sf.set_data(y_positions, SF)
            self.text_pos.set_text(f"p1 = {p1:.2f} m, p2 = {p2:.2f} m")
            return self.line_bm, self.line_sf, self.text_pos
        
        # Create and start animation; blit is set to False to update the entire canvas.
        self.animation = FuncAnimation(self.canvas.fig, update, frames=self.num_frames,
                                       interval=100, blit=False, repeat=True)
        self.canvas.draw()

###############################################
# Main Execution
###############################################

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
