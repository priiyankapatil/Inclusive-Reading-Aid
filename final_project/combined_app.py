import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFrame,
    QSlider, QFormLayout, QComboBox
)
from PyQt6.QtGui import QFont, QFontDatabase, QTextBlockFormat, QTextCursor
from PyQt6.QtCore import Qt

# Import PDF and Image processing libraries
import PyPDF2
from PIL import Image, ImageGrab

# Import OCR library
import pytesseract

class InclusiveReadingAidApp(QMainWindow):
    """
    Combined Inclusive Reading Aid Application
    Integrates both input handling and display customization features.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the main User Interface with both input and display features."""
        # Configure the main window
        self.setWindowTitle("Inclusive Reading Aid - Combined App")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create main vertical layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create input button panel at the top
        self._create_input_button_panel(main_layout)
        
        # Set up the main text area
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Open a file or capture screen to see text here...")
        
        # Initial placeholder text
        self.text_area.setText(
            "Welcome to Inclusive Reading Aid!\n\n"
            "Use the buttons above to:\n"
            "• Open text files (.txt)\n"
            "• Open PDF files (.pdf)\n"
            "• Open image files for OCR\n"
            "• Capture screen content\n\n"
            "Use the controls below to customize the display for better readability."
        )
        
        # Add text area to layout with stretch
        main_layout.addWidget(self.text_area, 1)
        
        # Create display customization controls at the bottom
        self._create_display_controls(main_layout)
        
        # Apply initial styling
        self.update_style()

    def _create_input_button_panel(self, main_layout):
        """
        Create a panel with input/file handling buttons.
        """
        # Create a frame for the button panel
        button_frame = QFrame()
        button_frame.setMaximumHeight(80)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        # Create horizontal layout for buttons
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 10, 20, 10)
        
        # Add stretch to center the buttons
        button_layout.addStretch()
        
        # Create styled buttons
        btn_style = """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
        
        # Open Text File button
        btn_text = QPushButton("📄 Open Text File")
        btn_text.setStyleSheet(btn_style)
        btn_text.setToolTip("Open a plain text file")
        btn_text.clicked.connect(self.open_text_file)
        button_layout.addWidget(btn_text)
        
        # Open PDF File button
        btn_pdf = QPushButton("📋 Open PDF File")
        btn_pdf.setStyleSheet(btn_style)
        btn_pdf.setToolTip("Open a PDF file")
        btn_pdf.clicked.connect(self.open_pdf_file)
        button_layout.addWidget(btn_pdf)
        
        # Open Image File button
        btn_image = QPushButton("🖼️ Open Image (OCR)")
        btn_image.setStyleSheet(btn_style)
        btn_image.setToolTip("Open an image file for OCR")
        btn_image.clicked.connect(self.open_image_file)
        button_layout.addWidget(btn_image)
        
        # Capture Screen button
        btn_capture = QPushButton("📸 Capture Screen")
        btn_capture.setStyleSheet(btn_style + """
            QPushButton {
                background-color: #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        btn_capture.setToolTip("Capture fullscreen for OCR")
        btn_capture.clicked.connect(self.capture_fullscreen_ocr)
        button_layout.addWidget(btn_capture)
        
        # Add stretch to center the buttons
        button_layout.addStretch()
        
        # Add the button frame to main layout
        main_layout.addWidget(button_frame)

    def _create_display_controls(self, main_layout):
        """
        Create display customization controls at the bottom.
        """
        # Create a frame for the controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        # Create layout for controls
        controls_layout = QFormLayout(controls_frame)
        
        # Font size slider
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(12, 48)
        self.font_size_slider.setValue(16)
        controls_layout.addRow("Font Size:", self.font_size_slider)

        # Line spacing slider
        self.line_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_spacing_slider.setRange(100, 300)  # 100% to 300%
        self.line_spacing_slider.setValue(100)
        controls_layout.addRow("Line Spacing:", self.line_spacing_slider)

        # Letter spacing slider
        self.letter_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.letter_spacing_slider.setRange(0, 20)  # 0px to 20px
        self.letter_spacing_slider.setValue(0)
        controls_layout.addRow("Letter Spacing:", self.letter_spacing_slider)

        # Font family dropdown
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "OpenDyslexic", 
            "Arial", 
            "Verdana", 
            "Times New Roman", 
            "Lexend"
        ])
        controls_layout.addRow("Font:", self.font_combo)

        # Theme dropdown
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Light (Default)", 
            "Dark", 
            "Yellow on Black", 
            "Blue on Cream"
        ])
        controls_layout.addRow("Theme:", self.theme_combo)

        # Connect controls to update function
        self.font_size_slider.valueChanged.connect(self.update_style)
        self.line_spacing_slider.valueChanged.connect(self.update_style)
        self.letter_spacing_slider.valueChanged.connect(self.update_style)
        self.font_combo.currentTextChanged.connect(self.update_style)
        self.theme_combo.currentTextChanged.connect(self.update_style)
        
        # Add controls frame to main layout
        main_layout.addWidget(controls_frame)

    def update_style(self):
        """
        Update the text area styling based on control values.
        """        # Get values from controls
        font_size = self.font_size_slider.value()
        line_spacing = self.line_spacing_slider.value()
        letter_spacing = self.letter_spacing_slider.value()
        font_family = self.font_combo.currentText()
        theme = self.theme_combo.currentText()

        # Set theme colors
        if theme == "Dark":
            bg_color = "#2b2b2b"
            text_color = "#ffffff"
        elif theme == "Yellow on Black":
            bg_color = "#000000"
            text_color = "#ffff00"
        elif theme == "Blue on Cream":
            bg_color = "#FDF5E6"  # Cream
            text_color = "#00008B"  # Dark Blue
        else:  # Light (Default)
            bg_color = "#ffffff"
            text_color = "#000000"        # Apply styles using CSS with improved color handling
        self.text_area.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color} !important;
                letter-spacing: {letter_spacing}px;
                font-size: {font_size}pt;
                font-family: {font_family};
                padding: 15px;
                border: 1px solid #ccc;
                border-radius: 8px;
                selection-background-color: rgba(0, 120, 215, 0.3);
                selection-color: {text_color};
            }}
            QTextEdit:focus {{
                color: {text_color} !important;
            }}
            """
        )

        # Handle line spacing separately using QTextDocument formatting
        document = self.text_area.document()
        line_spacing_multiplier = line_spacing / 100.0
        
        # Save current cursor position
        current_cursor = self.text_area.textCursor()
        current_position = current_cursor.position()
        
        # Select all text to apply formatting
        cursor = QTextCursor(document)
        cursor.select(QTextCursor.SelectionType.Document)
        
        # Create block format with line height
        block_format = QTextBlockFormat()
        block_format.setLineHeight(line_spacing_multiplier * 100, 1)  # 1 = ProportionalHeight
        
        # Apply the formatting
        cursor.mergeBlockFormat(block_format)
        
        # Restore cursor position
        new_cursor = self.text_area.textCursor()
        new_cursor.setPosition(current_position)
        self.text_area.setTextCursor(new_cursor)

    def _show_error(self, title, message):
        """
        Display an error message in a popup dialog and in the text area.
        """
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            print(f"Error showing message box: {e}")
            
        self.text_area.setPlainText(f"--- ERROR ---\n{message}")
        # Apply styling after setting error text
        self.update_style()

    # --- Input Logic Methods ---

    def open_text_file(self):
        """
        Handle opening and reading a plain .txt file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                    self.update_style()  # Apply current styling
            except Exception as e:
                self._show_error("File Read Error", f"Could not read the text file:\n{e}")

    def open_pdf_file(self):
        """
        Handle opening and extracting text from a .pdf file.
        """
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
                self.update_style()  # Apply current styling
            except Exception as e:
                self._show_error("PDF Read Error", f"Could not read the PDF file:\n{e}")

    def open_image_file(self):
        """
        Handle opening an image file and extracting text via OCR.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            try:
                # Open the image using Pillow
                img = Image.open(file_path)
                
                # Use pytesseract to extract text
                text = pytesseract.image_to_string(img)
                
                self.text_area.setPlainText(text)
                self.update_style()  # Apply current styling

            except pytesseract.TesseractNotFoundError:
                error_msg = (
                    "Tesseract OCR engine not found.\n\n"
                    "Please make sure Tesseract is installed on your system "
                    "and accessible in your system's PATH."
                )
                self._show_error("Tesseract Not Found", error_msg)
            except Exception as e:
                self._show_error("Image OCR Error", f"Could not process the image file:\n{e}")

    def capture_fullscreen_ocr(self):
        """
        Capture the entire screen and perform OCR on it.
        """
        try:
            # 1. Hide the main window
            self.hide()
            
            # Give the window a moment to hide
            time.sleep(0.5) 

            # 2. Grab the fullscreen screenshot
            screenshot = ImageGrab.grab()

            # 3. Restore the main window
            self.show()

            # 4. Process the image with Tesseract
            text = pytesseract.image_to_string(screenshot)
            
            # 5. Display the text
            self.text_area.setPlainText(text)
            self.update_style()  # Apply current styling

        except pytesseract.TesseractNotFoundError:
            self.show()  # Make sure window is shown if error happens early
            error_msg = (
                "Tesseract OCR engine not found.\n\n"
                "Please make sure Tesseract is installed on your system "
                "and accessible in your system's PATH."
            )
            self._show_error("Tesseract Not Found", error_msg)
        except Exception as e:
            self.show()  # Make sure window is shown on error
            self._show_error("Screen Capture Error", f"Could not capture or process the screen:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Try to load OpenDyslexic font
    font_path = "fonts/OpenDyslexic-Regular.otf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Warning: Could not load font from {font_path}")
    
    # Create and show the main window
    main_window = InclusiveReadingAidApp()
    main_window.show()
    
    sys.exit(app.exec())
