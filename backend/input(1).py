import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFrame
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

# Import PDF and Image processing libraries (Section 2.0 of report)
import PyPDF2
from PIL import Image, ImageGrab

# Import OCR library (Section 2.0 of report)
import pytesseract

class DyslexiaReaderApp(QMainWindow):
    """
    Main application window for the Inclusive Reading Aid.
    This class implements Module 1: Input Handling, as described
    in the project report.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the main User Interface."""
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create main vertical layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create centered button panel
        self._create_button_panel(main_layout)
        
        # Set up the main text area
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Open a file or capture screen to see text here...")
        self.text_area.setReadOnly(True)
        
        # Set stylesheet, including the fix for black text
        self.text_area.setStyleSheet("""
            QTextEdit {
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                line-height: 1.5;
                padding: 10px;
                background-color: #fdfdfd;
                border: 1px solid #ccc;
                border-radius: 8px;
                color: #000000; 
            }
        """)
        
        # Add text area to layout
        main_layout.addWidget(self.text_area, 1)  # stretch factor of 1

        # Configure the main window
        self.setWindowTitle("inclusive-reading-aid")
        self.setGeometry(100, 100, 800, 600)

    def _create_button_panel(self, main_layout):
        """
        Create a centered panel with upload/capture buttons.
        Replaces the traditional menu bar for better UX.
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
        btn_text.setToolTip("Open a plain text file (Ctrl+O)")
        btn_text.clicked.connect(self.open_text_file)
        button_layout.addWidget(btn_text)
        
        # Open PDF File button
        btn_pdf = QPushButton("📋 Open PDF File")
        btn_pdf.setStyleSheet(btn_style)
        btn_pdf.setToolTip("Open a PDF file (Ctrl+P)")
        btn_pdf.clicked.connect(self.open_pdf_file)
        button_layout.addWidget(btn_pdf)
        
        # Open Image File button
        btn_image = QPushButton("🖼️ Open Image (OCR)")
        btn_image.setStyleSheet(btn_style)
        btn_image.setToolTip("Open an image file for OCR (Ctrl+I)")
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
        btn_capture.setToolTip("Capture fullscreen for OCR (Ctrl+Shift+C)")
        btn_capture.clicked.connect(self.capture_fullscreen_ocr)
        button_layout.addWidget(btn_capture)
        
        # Add stretch to center the buttons
        button_layout.addStretch()
          # Add the button frame to main layout
        main_layout.addWidget(button_frame)

    def _show_error(self, title, message):
        """
Displays an error message in a popup dialog and in the text area.
This is part of the error handling described in Section 3.4.
"""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            # Fallback if GUI is not ready
            print(f"Error showing message box: {e}")
            
        self.text_area.setPlainText(f"--- ERROR ---\n{message}")

    # --- Input Logic (Section 3.2) ---

    def open_text_file(self):
        """
        Handles opening and reading a plain .txt file.
        Corresponds to Section 3.2.1.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
            except Exception as e:
                self._show_error("File Read Error", f"Could not read the text file:\n{e}")

    def open_pdf_file(self):
        """
        Handles opening and extracting text from a .pdf file.
        Corresponds to Section 3.2.2.
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
            except Exception as e:
                self._show_error("PDF Read Error", f"Could not read the PDF file:\n{e}")

    def open_image_file(self):
        """
        Handles opening an image file and extracting text via OCR.
        Corresponds to Section 3.2.3.
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

            except pytesseract.TesseractNotFoundError:
                # Specific error handling from Section 3.4
                error_msg = (
                    "Tesseract OCR engine not found.\n\n"
                    "Please make sure Tesseract is installed on your system "
                    "and accessible in your system's PATH."
                )
                self._show_error("Tesseract Not Found", error_msg)
            except Exception as e:
                # General error handling from Section 3.4
                self._show_error("Image OCR Error", f"Could not process the image file:\n{e}")

    # --- Screen Capture Logic (Section 3.3) ---

    def capture_fullscreen_ocr(self):
        """
        Captures the entire screen and performs OCR on it.
        Corresponds to Section 3.3.
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

        except pytesseract.TesseractNotFoundError:
            # Specific error handling from Section 3.4
            self.show() # Make sure window is shown if error happens early
            error_msg = (
                "Tesseract OCR engine not found.\n\n"
                "Please make sure Tesseract is installed on your system "
                "and accessible in your system's PATH."
            )
            self._show_error("Tesseract Not Found", error_msg)
        except Exception as e:
            # General error handling from Section 3.4
            self.show() # Make sure window is shown on error
            self._show_error("Screen Capture Error", f"Could not capture or process the screen:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DyslexiaReaderApp()
    main_window.show()
    sys.exit(app.exec())