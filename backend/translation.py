import sys
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QLabel, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import (
    QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
)

# Make sure to install the required libraries:
# pip install PyQt6 argostranslate
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    print("argostranslate library not found. Please install with: pip install argostranslate")
    ARGOS_AVAILABLE = False

# --- Worker Signals ---
# A QObject subclass is the standard way to define signals
# that can be emitted from a QRunnable (which can't emit signals directly).

class InitWorkerSignals(QObject):
    """
    Defines signals for the Initialization Worker.
    
    Signals:
        finished: Emits a dict of {language_name: language_code} when complete.
        error: Emits an error message (str) if initialization fails.
        status_update: Emits a progress message (str).
    """
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)

class TranslateWorkerSignals(QObject):
    """
    Defines signals for the Translation Worker.
    
    Signals:
        finished: Emits the translated text (str).
        error: Emits an error message (str) if translation fails.
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


# --- Worker Threads (QRunnable) ---

class InitWorker(QRunnable):
    """
    Worker thread to initialize translation models on startup.
    This runs argostranslate.package.update_package_index()
    and installs a few default language models.
    """
    def __init__(self):
        super().__init__()
        self.signals = InitWorkerSignals()
        
        # --- Languages to auto-install on first run ---
        # We target translations FROM English ('en')
        self.required_packages = {
            "en_es": False, # English to Spanish
            "en_fr": False, # English to French
            "en_de": False, # English to German
        }

    @pyqtSlot()
    def run(self):
        """
        The main logic for the initialization thread.
        This runs in the background.
        """
        try:
            # 1. Update the package index (download list of available models)
            self.signals.status_update.emit("Updating translation model index...")
            argostranslate.package.update_package_index()
            
            # 2. Check which models are already installed
            self.signals.status_update.emit("Checking installed models...")
            installed_packages = argostranslate.package.get_installed_packages()
            installed_names = set()
            for pkg in installed_packages:
                # The package name is like "translate-en_es-1.0"
                # We just want the "en_es" part
                pkg_codes = f"{pkg.from_code}_{pkg.to_code}"
                if pkg_codes in self.required_packages:
                    self.required_packages[pkg_codes] = True
                    installed_names.add(pkg.name)

            # 3. Install any missing models
            packages_to_install = []
            if not all(self.required_packages.values()):
                available_packages = argostranslate.package.get_available_packages()
                for pkg in available_packages:
                    pkg_codes = f"{pkg.from_code}_{pkg.to_code}"
                    if pkg_codes in self.required_packages and not self.required_packages[pkg_codes]:
                        packages_to_install.append(pkg)
                        
            if packages_to_install:
                self.signals.status_update.emit(f"Downloading {len(packages_to_install)} new models...")
                for pkg in packages_to_install:
                    self.signals.status_update.emit(f"Installing {pkg.name}...")
                    pkg.install()

            # 4. Get the final list of available translations (from English)
            self.signals.status_update.emit("Loading available languages...")
            installed_translations = argostranslate.translate.get_installed_translations()
            
            # We only care about translations FROM English ('en')
            from_en_translations = [t for t in installed_translations if t.from_lang.code == 'en']
            
            # Create the dictionary: {Language Name: language_code}
            # e.g., {"Spanish": "es", "French": "fr"}
            lang_dict = {t.to_lang.name: t.to_lang.code for t in from_en_translations}
            
            # 5. Emit the 'finished' signal with the language dictionary
            self.signals.finished.emit(lang_dict)

        except Exception as e:
            # On error, emit the error signal
            error_str = f"Initialization Error: {e}\n{traceback.format_exc()}"
            self.signals.error.emit(error_str)


class TranslateWorker(QRunnable):
    """
    Worker thread to perform a single translation task.
    """
    def __init__(self, text, from_code, to_code):
        super().__init__()
        self.signals = TranslateWorkerSignals()
        self.text = text
        self.from_code = from_code
        self.to_code = to_code

    @pyqtSlot()
    def run(self):
        """
        The main logic for the translation thread.
        This runs in the background.
        """
        try:
            # 1. Find the installed translation model
            translation = argostranslate.translate.get_translation_from_codes(
                self.from_code, self.to_code
            )
            
            if translation is None:
                raise RuntimeError(f"No translation model found for {self.from_code} -> {self.to_code}")

            # 2. Perform the translation
            translated_text = translation.translate(self.text)
            
            # 3. Emit the 'finished' signal with the result
            self.signals.finished.emit(translated_text)

        except Exception as e:
            # On error, emit the error signal
            error_str = f"Translation Error: {e}\n{traceback.format_exc()}"
            self.signals.error.emit(error_str)


# --- Main Application ---

class TranslationApp(QMainWindow):
    """
    The main application window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline Translation App (from Scratch)")
        self.setGeometry(100, 100, 800, 600)

        # QThreadPool is the modern way to manage worker threads
        self.threadpool = QThreadPool()
        print(f"Multithreading with max {self.threadpool.maxThreadCount()} threads")

        self.progress_dialog = None # For the "Processing..." dialog
        self.installed_languages = {} # To store {Name: code}
        
        # --- Main UI Setup ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Controls (Language Selection) ---
        controls_layout = QHBoxLayout()
        
        self.language_label = QLabel("Translate English to:")
        controls_layout.addWidget(self.language_label)
        
        self.language_combo = QComboBox()
        controls_layout.addWidget(self.language_combo)
        
        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.start_translation_task)
        controls_layout.addWidget(self.translate_button)
        
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # --- Text Areas (Input and Output) ---
        text_layout = QHBoxLayout()
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter English text to translate...")
        text_layout.addWidget(self.input_text)
        
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Translation will appear here...")
        self.output_text.setReadOnly(True)
        text_layout.addWidget(self.output_text)
        
        main_layout.addLayout(text_layout)

        # --- Status Bar ---
        self.statusBar().showMessage("Initializing translation models...")
        
        # --- Initial State (Disabled) ---
        # Keep controls disabled until models are loaded, as per the PDF
        self.language_combo.setEnabled(False)
        self.translate_button.setEnabled(False)
        self.language_combo.addItem("Loading models...")
        
        if not ARGOS_AVAILABLE:
            self.show_error_message(
                "ArgosTranslate Library Not Found",
                "Please install 'argostranslate' to run this application:\n\n"
                "pip install argostranslate"
            )
            self.statusBar().showMessage("Error: argostranslate not found.")
        else:
            # Start the background initialization
            self.start_init_worker()

    def start_init_worker(self):
        """
        Creates and starts the InitWorker in the thread pool.
        """
        worker = InitWorker()
        # Connect signals from the worker to slots in this (main) thread
        worker.signals.finished.connect(self.on_init_finished)
        worker.signals.error.connect(self.on_init_error)
        worker.signals.status_update.connect(self.on_init_status_update)
        
        # Start the worker. Its run() method will be called in a background thread.
        self.threadpool.start(worker)

    def start_translation_task(self):
        """
        Slot for the "Translate" button. Starts the TranslateWorker.
        This runs in the MAIN thread.
        """
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            return

        # 1. Get selected language name (e.g., "Spanish")
        selected_lang = self.language_combo.currentText()
        
        # 2. Look up its code (e.g., "es")
        to_code = self.installed_languages.get(selected_lang)
        
        if not to_code:
            self.show_error_message("Error", f"Could not find code for {selected_lang}")
            return
            
        from_code = "en" # Hardcoded as per the PDF

        # 3. Create and start the worker
        worker = TranslateWorker(input_text, from_code, to_code)
        worker.signals.finished.connect(self.on_translation_finished)
        worker.signals.error.connect(self.on_translation_error)
        self.threadpool.start(worker)

        # 4. Show the "Processing..." dialog
        self.show_progress_dialog("Translating", "Translating text... Please wait.")
        self.translate_button.setEnabled(False) # Disable button

    # --- Slots for Worker Signals ---
    # These methods are called when a worker emits a signal.
    # They run in the MAIN thread, so they can safely update the UI.

    @pyqtSlot(str)
    def on_init_status_update(self, status):
        """Updates the status bar with progress from the init worker."""
        self.statusBar().showMessage(status)

    @pyqtSlot(dict)
    def on_init_finished(self, lang_dict):
        """
        Slot for InitWorker's 'finished' signal.
        Populates the language dropdown.
        """
        self.installed_languages = lang_dict
        self.language_combo.clear()
        
        if not lang_dict:
            self.language_combo.addItem("No 'en' models found")
            self.statusBar().showMessage("Initialization complete. No English translation models found.")
            self.show_error_message(
                "No Models Found",
                "No English translation models (e.g., en_es, en_fr) were found.\n"
                "Please check your internet connection and restart."
            )
        else:
            # Populate dropdown
            self.language_combo.addItems(sorted(lang_dict.keys()))
            # Enable controls
            self.language_combo.setEnabled(True)
            self.translate_button.setEnabled(True)
            self.statusBar().showMessage("Ready to translate.")

    @pyqtSlot(str)
    def on_init_error(self, error_msg):
        """Slot for InitWorker's 'error' signal."""
        print(error_msg) # Print full error to console
        self.language_combo.clear()
        self.language_combo.addItem("Error")
        self.statusBar().showMessage("Initialization failed. See console for details.")
        self.show_error_message("Initialization Failed",
                                "Could not initialize translation models.\n"
                                "Please check your internet connection and restart.")

    @pyqtSlot(str)
    def on_translation_finished(self, translated_text):
        """Slot for TranslateWorker's 'finished' signal."""
        self.close_progress_dialog()
        self.output_text.setText(translated_text)
        self.translate_button.setEnabled(True) # Re-enable button

    @pyqtSlot(str)
    def on_translation_error(self, error_msg):
        """Slot for TranslateWorker's 'error' signal."""
        print(error_msg) # Print full error to console
        self.close_progress_dialog()
        self.show_error_message("Translation Failed",
                                "An error occurred during translation.")
        self.translate_button.setEnabled(True) # Re-enable button

    # --- Utility Dialog Methods ---

    def show_progress_dialog(self, title, text):
        """Shows a non-blocking, indeterminate progress dialog."""
        if not self.progress_dialog:
            self.progress_dialog = QProgressDialog(self)
            self.progress_dialog.setWindowTitle(title)
            self.progress_dialog.setModal(True)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.setRange(0, 0) # Indeterminate "busy"
            self.progress_dialog.setFixedSize(300, 100)
            
        self.progress_dialog.setLabelText(text)
        self.progress_dialog.show()

    def close_progress_dialog(self):
        """Hides the progress dialog."""
        if self.progress_dialog:
            self.progress_dialog.hide()

    def show_error_message(self, title, message):
        """Shows a standard error message box."""
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.setText(message)
        dlg.exec()

    def closeEvent(self, event):
        """Ensure threads are cleaned up on exit."""
        self.threadpool.clear() # Stop queued tasks
        self.threadpool.waitForDone() # Wait for active tasks to finish
        event.accept()


# --- Main execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec())