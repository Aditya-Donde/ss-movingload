# Beam Analysis with Moving Loads using Influence Line Diagrams

This project simulates and analyzes the shear force and bending moment of a simply supported beam under a moving load system. It uses the concept of **Influence Line Diagrams (ILD)** to calculate maximum internal forces, and provides animated visualizations and a user-friendly **PyQt GUI** for interaction.

---

## 🚀 Features

- Calculate maximum reactions at supports A and B
- Compute bending moment and shear force at specific points
- Determine maximum shear force and bending moment with their positions
- Visualize shear force and bending moment distributions dynamically as the load moves
- PyQt GUI for user input and real-time animated plotting using `matplotlib`

---

## 📥 Installation

Clone the repository:

```bash
git clone https://github.com/Aditya-Donde/ss-movingload.git
cd analyze_ss_movingload
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the application:

```bash
python main.py
```

### Inputs (entered through the GUI):
- **Length of Beam (L)** in meters
- **Moving Load Values (W1, W2)** in kN
- **Distance (x)** between W1 and W2 in meters

### Outputs (displayed in GUI):
- Maximum Reaction at A and B
- Bending Moment at W1 = 0 m (BM_01)
- Shear Force at mid-span (SF_01)
- Maximum Shear Force (SF_max) and its location
- Maximum Bending Moment (BM_max) and its location

The left panel displays **animated plots** of:
- Shear Force Distribution
- Bending Moment Distribution

as the load moves across the beam.

---

## 📁 File Structure

```
├── analyze_ss_movingload.py       
├── requirements.txt         
└── README.md                
```

---

## 🧠 Concepts Used

- Simply Supported Beam under Moving Loads
- Influence Line Diagrams (ILD)
- Structural Analysis using Python
- GUI development using PyQt5
- Animated plotting with Matplotlib

---

## 📸 Preview



---

## 📄 License

This project is licensed under the MIT License.
