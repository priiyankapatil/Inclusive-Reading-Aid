import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QKeySequence

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
        self.setCentralWidget(self.text_area)

        # Create the menu bar as described in section 3.1
        self._create_menu_bar()

        # Configure the main window
        self.setWindowTitle("inclusive-reading-aid")
        self.setGeometry(100, 100, 800, 600)

    def _create_menu_bar(self):
        """
        Helper function to create the main menu bar.
        Corresponds to Section 3.1 of the report.
        """
        menu_bar = self.menuBar()

        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")

        # "Open Text File..." action
        open_text_action = QAction("&Open Text File...", self)
        open_text_action.setShortcut(QKeySequence("Ctrl+O"))
        open_text_action.triggered.connect(self.open_text_file)
        file_menu.addAction(open_text_action)

        # "Open PDF File..." action
        open_pdf_action = QAction("Open &PDF File...", self)
        open_pdf_action.setShortcut(QKeySequence("Ctrl+P"))
        open_pdf_action.triggered.connect(self.open_pdf_file)
        file_menu.addAction(open_pdf_action)

        # "Open Image File (OCR)..." action
        open_image_action = QAction("Open &Image File (OCR)...", self)
        open_image_action.setShortcut(QKeySequence("Ctrl+I"))
        open_image_action.triggered.connect(self.open_image_file)
        file_menu.addAction(open_image_action)

        file_menu.addSeparator()

        # "Exit" action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Tools Menu ---
        tools_menu = menu_bar.addMenu("&Tools")

        # "Capture Fullscreen (OCR)" action
        capture_action = QAction("&Capture Fullscreen (OCR)", self)
        capture_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        capture_action.triggered.connect(self.capture_fullscreen_ocr)
        tools_menu.addAction(capture_action)

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