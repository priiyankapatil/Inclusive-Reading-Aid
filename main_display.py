import sys
import time  
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QSlider, QFormLayout, QComboBox,
    QFileDialog, QMessageBox  
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QAction, QKeySequence 

# --- NEW LIBRARIES FROM main.py ---
import PyPDF2
from PIL import Image, ImageGrab
import pytesseract
# --- END NEW LIBRARIES ---


# This class now contains BOTH your UI controls and your friend's input logic
class DyslexiaReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Step 1: Create the Basic Application Window ---
        self.setWindowTitle("Inclusive Reading Aid")
        self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)

        # --- MERGED: Create Menu Bar (from main.py) ---
        self._create_menu_bar()

        # Create a central widget and a layout for it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout (controls on bottom, text on top)
        main_layout = QVBoxLayout(central_widget)

        # --- Step 2: Add the Main Text Display Area ---
        self.text_area = QTextEdit()
        main_layout.addWidget(self.text_area, 1) # The '1' makes it take most of the space

        # --- MERGED: Set properties from both files ---
        self.text_area.setPlaceholderText("Use File > Open... or Tools > Capture... to load text here.")
        self.text_area.setReadOnly(True) 
        
        dyslexic_font = QFont("OpenDyslexic", 16) 
        self.text_area.setFont(dyslexic_font)

        # --- Step 4: Create the Customization Controls (Your Code) ---
        controls_layout = QFormLayout()

        self.line_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_spacing_slider.setRange(100, 300) 
        self.line_spacing_slider.setValue(100)
        controls_layout.addRow("Line Spacing:", self.line_spacing_slider)

        self.letter_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.letter_spacing_slider.setRange(0, 20)
        self.letter_spacing_slider.setValue(0)
        controls_layout.addRow("Letter Spacing:", self.letter_spacing_slider)
        
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(12, 48)
        self.font_size_slider.setValue(16)
        controls_layout.addRow("Font Size:", self.font_size_slider)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light (Default)", "Dark", "Yellow on Black", "Blue on Cream"])
        controls_layout.addRow("Theme:", self.theme_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "OpenDyslexic", "Arial", "Verdana", "Times New Roman", "Lexend"
        ])
        controls_layout.addRow("Font:", self.font_combo)

        main_layout.addLayout(controls_layout)

        # --- Step 5: Connect Controls (Your Code) ---
        self.line_spacing_slider.valueChanged.connect(self.update_style)
        self.letter_spacing_slider.valueChanged.connect(self.update_style)
        self.font_size_slider.valueChanged.connect(self.update_style)
        self.theme_combo.currentTextChanged.connect(self.update_style)
        self.font_combo.currentTextChanged.connect(self.update_style)

        # Apply the initial default style
        self.update_style()

    # --- This is YOUR update_style method ---
    def update_style(self):
        line_spacing = self.line_spacing_slider.value()
        letter_spacing = self.letter_spacing_slider.value()
        font_size = self.font_size_slider.value()
        theme = self.theme_combo.currentText()
        font_family = f"'{self.font_combo.currentText()}'"

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

    # --- ALL METHODS BELOW ARE COPIED FROM main.py ---

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        open_text_action = QAction("&Open Text File...", self)
        open_text_action.setShortcut(QKeySequence("Ctrl+O"))
        open_text_action.triggered.connect(self.open_text_file)
        file_menu.addAction(open_text_action)

        open_pdf_action = QAction("Open &PDF File...", self)
        open_pdf_action.setShortcut(QKeySequence("Ctrl+P"))
        open_pdf_action.triggered.connect(self.open_pdf_file)
        file_menu.addAction(open_pdf_action)

        open_image_action = QAction("Open &Image File (OCR)...", self)
        open_image_action.setShortcut(QKeySequence("Ctrl+I"))
        open_image_action.triggered.connect(self.open_image_file)
        file_menu.addAction(open_image_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menu_bar.addMenu("&Tools")

        capture_action = QAction("&Capture Fullscreen (OCR)", self)
        capture_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        capture_action.triggered.connect(self.capture_fullscreen_ocr)
        tools_menu.addAction(capture_action)

    def _show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        self.text_area.setPlainText(f"--- ERROR ---\n{message}")

    def open_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                    self.text_area.setReadOnly(False) # Allow editing text
            except Exception as e:
                self._show_error("File Read Error", f"Could not read the text file:\n{e}")

    def open_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            try:
                full_text = []
                reader = PyPDF2.PdfReader(file_path)
                for page in reader.pages:
                    full_text.append(page.extract_text())
                
                content = "\n".join(full_text)
                self.text_area.setPlainText(content)
                self.text_area.setReadOnly(True) # No editing PDFs
            except Exception as e:
                self._show_error("PDF Read Error", f"Could not read the PDF file:\n{e}")

    def open_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                self.text_area.setPlainText(text)
                self.text_area.setReadOnly(True) # No editing OCR
            except pytesseract.TesseractNotFoundError:
                error_msg = ("Tesseract OCR engine not found.\n\nPlease make sure Tesseract is installed.")
                self._show_error("Tesseract Not Found", error_msg)
            except Exception as e:
                self._show_error("Image OCR Error", f"Could not process the image file:\n{e}")

    def capture_fullscreen_ocr(self):
        try:
            self.hide()
            time.sleep(0.5) 
            screenshot = ImageGrab.grab()
            self.show()
            text = pytesseract.image_to_string(screenshot)
            self.text_area.setPlainText(text)
            self.text_area.setReadOnly(True) # No editing OCR
        except pytesseract.TesseractNotFoundError:
            self.show()
            error_msg = ("Tesseract OCR engine not found.\n\nPlease make sure Tesseract is installed.")
            self._show_error("Tesseract Not Found", error_msg)
        except Exception as e:
            self.show()
            self._show_error("Screen Capture Error", f"Could not capture or process the screen:\n{e}")


# --- This is YOUR main execution block, with font loading ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Load custom font ---
    font_path = "fonts/OpenDyslexic-Regular.otf" 
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Warning: Could not load font from {font_path}")

    window = DyslexiaReaderApp()
    window.show()
    sys.exit(app.exec())