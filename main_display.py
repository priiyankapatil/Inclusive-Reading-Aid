import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QSlider, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# This class will hold all our application logic
class DyslexiaReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Step 1: Create the Basic Application Window ---
        self.setWindowTitle("Inclusive Reading Aid")
        self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)

        # Create a central widget and a layout for it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout (controls on bottom, text on top)
        main_layout = QVBoxLayout(central_widget)

        # --- Step 2: Add the Main Text Display Area ---
        self.text_area = QTextEdit()
        main_layout.addWidget(self.text_area, 1) # The '1' makes it take most of the space

        # --- Step 3: Apply the OpenDyslexic Font ---
        # NOTE: You MUST have "OpenDyslexic" font installed on your OS!
        # We set the initial font here, but update_style() will control it
        dyslexic_font = QFont("OpenDyslexic", 16) # Font family, base size
        self.text_area.setFont(dyslexic_font)

        # --- Load some dummy text to see the changes ---
        self.text_area.setText(
            "This is a test of the OpenDyslexic font.\n\n"
            "Move the sliders to change the spacing. "
            "Use the dropdown to change the theme or font."
        )

        # --- Step 4: Create the Customization Controls ---
        # We use a QFormLayout for a tidy "label: widget" look
        controls_layout = QFormLayout()

        # Sliders for spacing
        self.line_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_spacing_slider.setRange(100, 300)  # 100% to 300%
        self.line_spacing_slider.setValue(100)
        controls_layout.addRow("Line Spacing:", self.line_spacing_slider)

        self.letter_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.letter_spacing_slider.setRange(0, 20)  # 0px to 20px
        self.letter_spacing_slider.setValue(0)
        controls_layout.addRow("Letter Spacing:", self.letter_spacing_slider)
        
        # Font size slider
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(12, 48) # 12pt to 48pt
        self.font_size_slider.setValue(16)
        controls_layout.addRow("Font Size:", self.font_size_slider)

        # Dropdown for themes
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light (Default)", "Dark", "Yellow on Black", "Blue on Cream"])
        controls_layout.addRow("Theme:", self.theme_combo)

        # --- NEW FONT DROPDOWN ---
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "OpenDyslexic", 
            "Arial", 
            "Verdana", 
            "Times New Roman", 
            "Lexend" # Another good font for readability
        ])
        controls_layout.addRow("Font:", self.font_combo)
        # --- END NEW FONT DROPDOWN ---

        # Add the controls layout to the main layout
        main_layout.addLayout(controls_layout)

        # --- Step 5: Connect Controls to the Text Display (The Logic) ---
        self.line_spacing_slider.valueChanged.connect(self.update_style)
        self.letter_spacing_slider.valueChanged.connect(self.update_style)
        self.font_size_slider.valueChanged.connect(self.update_style)
        self.theme_combo.currentTextChanged.connect(self.update_style)
        
        # --- CONNECT NEW FONT COMBO ---
        self.font_combo.currentTextChanged.connect(self.update_style)
        # --- END CONNECT NEW FONT COMBO ---

        # Apply the initial default style
        self.update_style()

    def update_style(self):
        """
        This is the main function that reads all controls 
        and applies the styling to the text area.
        """
        # Get values from controls
        line_spacing = self.line_spacing_slider.value()
        letter_spacing = self.letter_spacing_slider.value()
        font_size = self.font_size_slider.value()
        theme = self.theme_combo.currentText()
        
        # --- GET SELECTED FONT ---
        # We add quotes around the font name in case it has spaces
        font_family = f"'{self.font_combo.currentText()}'"
        # --- END GET SELECTED FONT ---


        # Set theme colors
        if theme == "Dark":
            bg_color = "black"
            text_color = "white"
        elif theme == "Yellow on Black":
            bg_color = "black"
            text_color = "yellow"
        elif theme == "Blue on Cream":
            bg_color = "#FDF5E6" # Cream
            text_color = "#00008B" # Dark Blue
        else: # Light (Default)
            bg_color = "white"
            text_color = "black"

        # Apply styles using CSS-like syntax
        # We also set the font-family here to ensure it's always applied
        self.text_area.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                line-height: {line_spacing}%;
                letter-spacing: {letter_spacing}px;
                font-size: {font_size}pt;
                font-family: {font_family};
            }}
            """
        )

# --- This is the standard code to run the application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DyslexiaReaderApp()
    window.show()
    sys.exit(app.exec())