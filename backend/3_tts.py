import sys
import time
import pyttsx3  # Module 3 Import
import threading  # Module 3 Import
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    # --- Module 3 GUI Imports ---
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QRadioButton, QGroupBox, QLabel
)
from PyQt6.QtGui import (
    QAction, QKeySequence,
    # --- Module 3 GUI Imports ---
    QTextCursor, QTextCharFormat, QColor
)
from PyQt6.QtCore import pyqtSignal, Qt  # Module 3 Import

# Import PDF and Image processing libraries (Section 2.0 of report)
import PyPDF2
from PIL import Image, ImageGrab

# Import OCR library (Section 2.0 of report)
import pytesseract


class InclusiveReadingAidApp(QMainWindow):
    """
    Main application window for the Inclusive Reading Aid.
    This class implements:
    - Module 1: Input Handling
    - Module 3: Audio Support (Text-to-Speech)
    """
    
    # --- Module 3: Thread-Safe Highlighting (Section 3.2) ---
    # Custom signal to send (location, length) from worker thread to main thread
    word_highlight_signal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        # --- Module 3: Highlighting Formats (Section 3.1) ---
        self.highlight_char_format = QTextCharFormat()
        self.highlight_char_format.setBackground(QColor("yellow"))
        self.highlight_char_format.setForeground(QColor("black"))
        
        self.normal_char_format = QTextCharFormat()
        # (Default colors are fine)

        # --- Module 3: Engine Initialization (Section 3.1) ---
        self._init_tts_engine()
        
        self.init_ui()
        
        # --- Module 3: Connect Signal to Slot (Section 3.2) ---
        self.word_highlight_signal.connect(self.highlight_word)

    def _init_tts_engine(self):
        """Helper function to initialize the TTS engine."""
        try:
            self.tts_engine = pyttsx3.init()
            # --- Module 3: TTS Event Hook (Section 3.2) ---
            self.tts_engine.connect('started-word', self._on_word_started)
        except Exception as e:
            self.tts_engine = None
            # Use _show_error later, as GUI isn't built yet
            print(f"FATAL: Could not initialize TTS engine: {e}")
            # We'll show this error when the GUI is ready

    def init_ui(self):
        """Initialize the main User Interface."""
        
        # --- Module 3: GUI Redesign ---
        # We need a main widget with a layout to hold the text area AND controls
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Set up the main text area (from Module 1)
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Open a file or capture screen to see text here...")
        self.text_area.setReadOnly(True)
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
        main_layout.addWidget(self.text_area, 1) # Add to layout (stretchable)

        # --- Module 3: Add Controls Panel (from Module 6) ---
        self.controls_panel = self._create_controls_panel()
        main_layout.addWidget(self.controls_panel) # Add to layout
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget) # Set the new main widget

        # Create the menu bar (from Module 1)
        self._create_menu_bar()

        # Configure the main window
        self.setWindowTitle("inclusive-reading-aid")
        self.setGeometry(100, 100, 800, 700) # Made window taller for controls

        # If TTS engine failed, show error now
        if not self.tts_engine:
            self._show_error("TTS Engine Failure", 
                             "Could not initialize the Text-to-Speech engine.\n"
                             "Please ensure you have a speech driver installed on your OS.")

    def _create_controls_panel(self):
        """Creates the GUI panel for Mode and Speed controls."""
        panel_widget = QWidget()
        panel_layout = QHBoxLayout()

        # --- Mode Controls ---
        mode_group = QGroupBox("Mode")
        mode_layout = QVBoxLayout()
        self.rb_read_only = QRadioButton("Read Only")
        self.rb_read_highlight = QRadioButton("Read with Highlights")
        self.rb_listen_only = QRadioButton("Listen Only")
        
        self.rb_read_only.setChecked(True) # Default mode
        
        # Connect to mode update function (Section 3.4)
        self.rb_read_only.toggled.connect(self.update_mode)
        self.rb_read_highlight.toggled.connect(self.update_mode)
        self.rb_listen_only.toggled.connect(self.update_mode)

        mode_layout.addWidget(self.rb_read_only)
        mode_layout.addWidget(self.rb_read_highlight)
        mode_layout.addWidget(self.rb_listen_only)
        mode_group.setLayout(mode_layout)

        # --- Speed Control (Section 3.3) ---
        speed_group = QGroupBox("Reading Speed")
        speed_layout = QVBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)  # 50% speed
        self.speed_slider.setMaximum(200) # 200% speed
        self.speed_slider.setValue(100)   # 100% default
        self.speed_slider.setSingleStep(10)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(50)
        
        self.speed_slider.valueChanged.connect(self.update_tts_speed)
        
        speed_layout.addWidget(self.speed_slider)
        speed_group.setLayout(speed_layout)
        
        # Initialize speed
        self.update_tts_speed(self.speed_slider.value())

        panel_layout.addWidget(mode_group)
        panel_layout.addWidget(speed_group, 1) # Make slider stretch
        panel_widget.setLayout(panel_layout)
        return panel_widget


    def _create_menu_bar(self):
        """(From Module 1, no changes)"""
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
        """(From Module 1, no changes)"""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            print(f"Error showing message box: {e}")
        self.text_area.setPlainText(f"--- ERROR ---\n{message}")

    # --- Module 3: New Highlighting & Audio Functions ---

    def clear_highlighting(self):
        """Resets all text to the normal format."""
        cursor = self.text_area.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(self.normal_char_format)
        cursor.clearSelection()
        self.text_area.setTextCursor(cursor)

    def _on_word_started(self, name, location, length):
        """
        WORKER THREAD function.
        Emits the word_highlight_signal with the word's position.
        (Section 3.2.3)
        """
        self.word_highlight_signal.emit(location, length)

    def highlight_word(self, location, length):
        """
        MAIN THREAD slot.
        Receives the signal and applies highlighting to the UI.
        (Section 3.2.4)
        """
        self.clear_highlighting()
        
        cursor = self.text_area.textCursor()
        cursor.setPosition(location)
        cursor.movePosition(QTextCursor.MoveOperation.Right, 
                            QTextCursor.MoveMode.KeepAnchor, 
                            length)
        cursor.setCharFormat(self.highlight_char_format)
        self.text_area.setTextCursor(cursor)

    def update_tts_speed(self, value):
        """
        Slot to update TTS speed from the slider.
        (Section 3.3.1)
        """
        if self.tts_engine:
            # Map slider (50-200) to a rate (e.g., 100-400 WPM)
            # Default rate is ~200. We'll map 100 -> 200.
            rate = value * 2 
            self.tts_engine.setProperty('rate', rate)

    def update_mode(self):
        """
        Slot to handle mode changes from radio buttons.
        (Section 3.4)
        """
        if not self.tts_engine:
            return # Do nothing if TTS failed

        # --- THIS IS THE FIX ---
        # Stop any currently running speech *before* deciding what to do next
        self.tts_engine.stop()
        # --- END OF FIX ---

        if self.rb_read_only.isChecked():
            # self.tts_engine.stop() # Moved to top
            self.text_area.show()
            self.clear_highlighting()
        
        elif self.rb_read_highlight.isChecked():
            self.text_area.show()
            self.start_tts()
            
        elif self.rb_listen_only.isChecked():
            self.text_area.hide()
            self.start_tts()

    def _play_tts_thread(self, text):
        """
        WORKER THREAD function. Runs the blocking TTS calls.
        (Section 3.3.2)
        """
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            # We'll print this error to the console for debugging
            print(f"Error in TTS thread: {e}")

    def start_tts(self):
        """
        Starts the TTS playback in a new thread.
        (Section 3.3.2)
        """
        if not self.tts_engine:
            self._show_error("TTS Error", "TTS Engine is not initialized.")
            return

        text = self.text_area.toPlainText()
        if text:
            # Run the blocking call in a separate thread
            # daemon=True ensures the thread exits when the main app exits
            t = threading.Thread(target=self._play_tts_thread, args=(text,), daemon=True)
            t.start()

    # --- Module 1: Input Logic (Updated for Module 3) ---
    
    def _load_new_text(self, content):
        """Helper to safely load text and reset UI."""
        if self.tts_engine:
            self.tts_engine.stop()
        self.clear_highlighting()
        self.text_area.setPlainText(content)
        # Reset mode to "Read Only"
        self.rb_read_only.setChecked(True)

    def open_text_file(self):
        """(Module 1) Handles .txt files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._load_new_text(content) # Use helper
            except Exception as e:
                self._show_error("File Read Error", f"Could not read the text file:\n{e}")

    def open_pdf_file(self):
        """(Module 1) Handles .pdf files."""
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
                # --- THIS IS THE FIX ---
                self._load_new_text(content) # Use helper
            except Exception as e:
                self._show_error("PDF Read Error", f"Could not read the PDF file:\n{e}")

    def open_image_file(self):
        """(Module 1) Handles image files with OCR."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        if file_path:
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                self._load_new_text(text) # Use helper
            except pytesseract.TesseractNotFoundError:
                # --- THIS IS THE FIX ---
                error_msg = (
                    "Tesseract OCR engine not found.\n\n"
                    "Please make sure Tesseract is installed on your system "
                    "and accessible in your system's PATH."
                )
                self._show_error("Tesseract Not Found", error_msg)
            except Exception as e:
                self._show_error("Image OCR Error", f"Could not process the image file:\n{e}")

    def capture_fullscreen_ocr(self):
        """(Module 1) Handles fullscreen OCR."""
        try:
            self.hide()
            time.sleep(0.5) 
            screenshot = ImageGrab.grab()
            self.show()
            text = pytesseract.image_to_string(screenshot)
            self._load_new_text(text) # Use helper
        except pytesseract.TesseractNotFoundError:
            self.show()
            error_msg = (
                "Tesseract OCR engine not found.\n\n"
                "Please make sure Tesseract is installed on your system "
                "and accessible in your system's PATH."
            )
            self._show_error("Tesseract Not Found", error_msg)
        except Exception as e:
            self.show()
            self._show_error("Screen Capture Error", f"Could not capture or process the screen:\n{e}")

    # --- Module 3: Ensure TTS stops on exit ---
    def closeEvent(self, event):
        """Overrides the close event to stop the TTS engine."""
        if self.tts_engine:
            self.tts_engine.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = InclusiveReadingAidApp()
    main_window.show()
    sys.exit(app.exec())