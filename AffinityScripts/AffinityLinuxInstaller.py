#!/usr/bin/env python3
"""
Affinity Linux Installer - PyQt6 GUI Version
A modern, professional GUI application for installing Affinity software on Linux
"""

import os
import sys
import subprocess
import shutil
import tarfile
import zipfile
import threading
import platform
import urllib.request
import urllib.error
from pathlib import Path
import time

# Function to detect Linux distribution
def detect_distro_for_install():
    """Detect distribution for package installation"""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
        for line in content.split("\n"):
            if line.startswith("ID="):
                return line.split("=", 1)[1].strip().strip('"').lower()
    except:
        pass
    return None

# Function to install Python package
def install_package(package_name, import_name=None):
    """Install a Python package if not available"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        print(f"Installing {package_name}...")
        
        # Try with --break-system-packages for PEP 668 systems
        distro = detect_distro_for_install()
        pip_flags = ["--user"]
        if distro in ["arch", "cachyos", "manjaro"]:
            pip_flags.append("--break-system-packages")
        # Add quiet only if we're not showing output
        if not sys.stdout.isatty():
            pip_flags.insert(0, "--quiet")
        
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name] + pip_flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            try:
                __import__(import_name)
                print(f"✓ {package_name} installed successfully")
                return True
            except ImportError:
                print(f"✗ Failed to import {package_name} after installation")
                return False
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package_name} via pip")
            return False
        except Exception as e:
            print(f"✗ Error installing {package_name}: {e}")
            return False

# Check and install PyQt6
PYQT6_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit, QFrame,
        QProgressBar, QGroupBox, QScrollArea, QDialog, QDialogButtonBox,
        QButtonGroup, QRadioButton
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
    from PyQt6.QtSvgWidgets import QSvgWidget
    PYQT6_AVAILABLE = True
except ImportError:
    print("PyQt6 not found. Attempting to install...")
    if install_package("PyQt6", "PyQt6"):
        try:
            from PyQt6.QtWidgets import (
                QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit, QFrame,
                QProgressBar, QGroupBox, QScrollArea, QDialog, QDialogButtonBox,
                QButtonGroup, QRadioButton
            )
            from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
            from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
            from PyQt6.QtSvgWidgets import QSvgWidget
            PYQT6_AVAILABLE = True
            print("✓ PyQt6 installed and imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import PyQt6 after installation: {e}")
            PYQT6_AVAILABLE = False
    else:
        print("✗ Failed to install PyQt6 via pip")
        PYQT6_AVAILABLE = False

if not PYQT6_AVAILABLE:
    print("\nERROR: PyQt6 is required but could not be installed.")
    print("Please install PyQt6 manually using one of these methods:\n")
    print("Using pip:")
    print("  pip install --user PyQt6")
    print("\nOr using your distribution's package manager:")
    print("  Arch/CachyOS: sudo pacman -S python-pyqt6")
    print("  Fedora/Nobara: sudo dnf install python3-qt6")
    print("  Debian/Ubuntu/Mint/Pop/Zorin/PikaOS: sudo apt install python3-pyqt6")
    print("  openSUSE: sudo zypper install python3-qt6")
    sys.exit(1)


class AffinityInstallerGUI(QMainWindow):
    # Signals for thread-safe GUI updates
    log_signal = pyqtSignal(str, str)  # message, level
    progress_signal = pyqtSignal(float)  # value (0.0-1.0)
    show_message_signal = pyqtSignal(str, str, str)  # title, message, type (info/error/warning)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Affinity Linux Installer")
        self.setGeometry(100, 100, 1200, 700)
        
        # Variables
        self.distro = None
        self.distro_version = None
        self.directory = str(Path.home() / ".AffinityLinux")
        self.setup_complete = False
        self.installer_file = None
        
        # Connect signals
        self.log_signal.connect(self._log_safe)
        self.progress_signal.connect(self._update_progress_safe)
        self.show_message_signal.connect(self._show_message_safe)
        
        # Load Affinity icon
        self.load_affinity_icon()
        
        # Setup UI
        self.create_ui()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Center window
        self.center_window()
        
        # Don't auto-start initialization - user will click button
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Affinity Linux Installer - Ready", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log("Welcome! Please use the buttons on the right to get started.", "info")
        self.log("Click 'Setup Wine Environment' to begin the installation process.", "info")
    
    def center_window(self):
        """Center window on screen"""
        frame = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
    
    def apply_dark_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: none;
                background-color: #252526;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #2d2d30;
                color: #cccccc;
                font-weight: bold;
                font-size: 11px;
            }
            QFrame {
                background-color: #252526;
                border: none;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 6px 12px;
                min-height: 28px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #464647;
                border-color: #5a5a5a;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
                border-color: #3a3a3a;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QProgressBar {
                border: none;
                background-color: #3c3c3c;
                height: 4px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
                border-radius: 2px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def create_ui(self):
        """Create the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #252526; padding: 15px 20px;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 15, 20, 15)
        
        # Add Affinity icon if available
        if hasattr(self, 'affinity_icon_path') and self.affinity_icon_path:
            try:
                # Try to use QSvgWidget for proper SVG rendering
                try:
                    # Set window icon
                    icon = QIcon(self.affinity_icon_path)
                    self.setWindowIcon(icon)
                    
                    # Use QSvgWidget for proper SVG display
                    svg_widget = QSvgWidget(self.affinity_icon_path)
                    svg_widget.setFixedSize(40, 40)  # Larger size to prevent cutoff
                    svg_widget.setStyleSheet("background: transparent;")
                    top_bar_layout.addWidget(svg_widget)
                    top_bar_layout.addSpacing(10)
                except:
                    # Fallback to QIcon if QSvgWidget fails
                    icon = QIcon(self.affinity_icon_path)
                    self.setWindowIcon(icon)
                    
                    icon_label = QLabel()
                    # Use larger size with proper scaling
                    pixmap = icon.pixmap(40, 40)
                    if not pixmap.isNull():
                        icon_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        icon_label.setFixedSize(40, 40)
                        top_bar_layout.addWidget(icon_label)
                        top_bar_layout.addSpacing(10)
            except Exception as e:
                pass  # If icon loading fails, continue without icon
        
        title = QLabel("Affinity Linux Installer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        top_bar_layout.addWidget(title)
        top_bar_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Status/Log
        left_panel = self.create_status_section()
        content_layout.addWidget(left_panel, stretch=2)
        
        # Right panel - Buttons
        right_panel = self.create_button_sections()
        content_layout.addWidget(right_panel, stretch=0)
        
        main_layout.addWidget(content_widget, stretch=1)
    
    def create_status_section(self):
        """Create the status/log output section"""
        group = QGroupBox("Status & Log Output")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(12, 25, 12, 12)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        group_layout.addWidget(self.progress)
        
        # Log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 11))
        group_layout.addWidget(self.log_text)
        
        return group
    
    def create_button_sections(self):
        """Create organized button sections"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Quick Start section - One-click install
        quick_group = self.create_button_group(
            "Quick Start",
            [
                ("One-Click Full Setup", self.one_click_setup),
            ]
        )
        container_layout.addWidget(quick_group)
        
        # System Setup section
        sys_group = self.create_button_group(
            "System Setup",
            [
                ("Setup Wine Environment", self.start_initialization),
                ("Install System Dependencies", self.install_system_dependencies),
                ("Install Winetricks Dependencies", self.install_winetricks_dependencies),
                ("Reinstall WinMetadata", self.reinstall_winmetadata),
                ("Install from File Manager", self.install_from_file),
            ]
        )
        container_layout.addWidget(sys_group)
        
        # Update Affinity Applications section
        app_group = self.create_button_group(
            "Update Affinity Applications",
            [
                ("Affinity (Unified)", lambda: self.update_application("Add")),
                ("Affinity Photo", lambda: self.update_application("Photo")),
                ("Affinity Designer", lambda: self.update_application("Designer")),
                ("Affinity Publisher", lambda: self.update_application("Publisher")),
            ]
        )
        container_layout.addWidget(app_group)
        
        # Troubleshooting section
        troubleshoot_group = self.create_button_group(
            "Troubleshooting",
            [
                ("Open Wine Configuration", self.open_winecfg),
                ("Set Windows 11 + Renderer", self.set_windows11_renderer),
            ]
        )
        container_layout.addWidget(troubleshoot_group)
        
        # Other section
        other_group = self.create_button_group(
            "Other",
            [
                ("Special Thanks", self.show_thanks),
                ("Exit", self.close),
            ]
        )
        container_layout.addWidget(other_group)
        
        container_layout.addStretch()
        
        return container
    
    def create_button_group(self, title, buttons):
        """Create a grouped button section"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(8, 20, 8, 8)
        
        for button_data in buttons:
            # Handle both (text, command) and (text, command, color) formats for backward compatibility
            if len(button_data) == 2:
                text, command = button_data
            else:
                text, command, _ = button_data
            
            btn = QPushButton(text)
            # All buttons now use neutral colors for better readability
            btn.clicked.connect(command)
            group_layout.addWidget(btn)
        
        return group
    
    def load_affinity_icon(self):
        """Download and load Affinity V3 icon"""
        try:
            icon_dir = Path.home() / ".local" / "share" / "icons"
            icon_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icon_dir / "Affinity.svg"
            
            # Download if not exists
            if not icon_path.exists():
                icon_url = "https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-V3.svg"
                try:
                    urllib.request.urlretrieve(icon_url, str(icon_path))
                    self.affinity_icon_path = str(icon_path)
                except Exception as e:
                    self.affinity_icon_path = None
            else:
                self.affinity_icon_path = str(icon_path)
        except Exception as e:
            self.affinity_icon_path = None
    
    def log(self, message, level="info"):
        """Add message to log (thread-safe via signal)"""
        self.log_signal.emit(message, level)
    
    def _log_safe(self, message, level="info"):
        """Thread-safe log handler (called from main thread)"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] "
        
        if level == "error":
            prefix += "✗ "
            color = "#f48771"
        elif level == "success":
            prefix += "✓ "
            color = "#4ec9b0"
        elif level == "warning":
            prefix += "⚠ "
            color = "#ce9178"
        else:
            prefix += "→ "
            color = "#d4d4d4"
        
        full_message = f'<span style="color: {color};">{prefix}{message}</span>'
        self.log_text.append(full_message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def update_progress(self, value):
        """Update progress bar (thread-safe via signal)"""
        self.progress_signal.emit(value)
    
    def _update_progress_safe(self, value):
        """Thread-safe progress update handler (called from main thread)"""
        self.progress.setValue(int(value * 100))
    
    def show_message(self, title, message, msg_type="info"):
        """Show message box (thread-safe via signal)"""
        self.show_message_signal.emit(title, message, msg_type)
    
    def _show_message_safe(self, title, message, msg_type="info"):
        """Thread-safe message box handler (called from main thread)"""
        if msg_type == "error":
            QMessageBox.critical(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        else:
            QMessageBox.information(self, title, message)
    
    def run_command(self, command, check=True, shell=False, capture=True, env=None):
        """Execute shell command"""
        try:
            if isinstance(command, str) and not shell:
                command = command.split()
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture,
                text=capture,
                check=check,
                env=env if env else os.environ.copy()
            )
            if capture:
                return result.returncode == 0, result.stdout, result.stderr
            return result.returncode == 0, "", ""
        except subprocess.CalledProcessError as e:
            return False, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else ""
        except Exception as e:
            return False, "", str(e)
    
    def check_command(self, cmd):
        """Check if command exists"""
        return shutil.which(cmd) is not None
    
    def detect_distro(self):
        """Detect Linux distribution"""
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read()
            
            for line in content.split("\n"):
                if line.startswith("ID="):
                    self.distro = line.split("=", 1)[1].strip().strip('"')
                elif line.startswith("VERSION_ID="):
                    self.distro_version = line.split("=", 1)[1].strip().strip('"')
            
            return True
        except Exception as e:
            self.log(f"Error detecting distribution: {e}", "error")
            return False
    
    def download_file(self, url, output_path, description=""):
        """Download file with progress tracking"""
        try:
            self.log(f"Downloading {description}...", "info")
            
            # Create request with proper headers
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            req.add_header('Accept', '*/*')
            
            # Use urlopen for better header support and manual progress tracking
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(output_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = min(100, (downloaded * 100) // total_size)
                            self.update_progress(percent / 100.0)
                
                self.update_progress(1.0)
                return True
        except urllib.error.HTTPError as e:
            self.log(f"Download failed: HTTP {e.code} {e.reason}", "error")
            if e.code == 404:
                self.log(f"  URL may be expired or invalid: {url[:80]}...", "warning")
            return False
        except Exception as e:
            self.log(f"Download failed: {e}", "error")
            return False
    
    def start_initialization(self):
        """Start initialization process"""
        threading.Thread(target=self.initialize, daemon=True).start()
    
    def initialize(self):
        """Initialize installer"""
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Affinity Linux Installer - Initialization", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Detect distribution
        self.update_progress(0.1)
        if not self.detect_distro():
            self.log("Failed to detect distribution. Exiting.", "error")
            return
        
        self.log(f"Detected distribution: {self.distro} {self.distro_version or ''}", "success")
        self.update_progress(0.2)
        
        # Check dependencies
        if not self.check_dependencies():
            return
        
        # Setup Wine
        self.update_progress(0.5)
        self.setup_wine()
        
        # Show main menu
        QTimer.singleShot(0, self.show_main_menu)
    
    def one_click_setup(self):
        """One-click full setup: detects distro, installs deps, sets up Wine, installs Winetricks deps"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("One-Click Full Setup", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log("This will automatically:", "info")
        self.log("  1. Detect your Linux distribution", "info")
        self.log("  2. Check and install system dependencies", "info")
        self.log("  3. Setup Wine environment (download and configure)", "info")
        self.log("  4. Install Winetricks dependencies (.NET, fonts, etc.)", "info")
        self.log("  5. Prompt you to install an Affinity application\n", "info")
        
        threading.Thread(target=self._one_click_setup_thread, daemon=True).start()
    
    def _one_click_setup_thread(self):
        """One-click setup in background thread"""
        # Step 1: Detect distribution
        self.update_progress(0.05)
        if not self.detect_distro():
            self.log("Failed to detect distribution. Cannot continue.", "error")
            return
        
        self.log(f"Detected distribution: {self.distro} {self.distro_version or ''}", "success")
        
        # Step 2: Check and install dependencies
        self.update_progress(0.15)
        if not self.check_dependencies():
            self.log("Dependency check failed. Please resolve issues and try again.", "error")
            return
        
        # Step 3: Setup Wine environment (this includes winetricks dependencies via configure_wine)
        self.update_progress(0.40)
        self.setup_wine()
        
        # Complete! (setup_wine already calls configure_wine which installs winetricks deps)
        self.update_progress(1.0)
        self.log("\n✓ Full setup completed!", "success")
        self.log("You can now install Affinity applications using the buttons above.", "info")
        
        # Ask if user wants to install an Affinity app
        QTimer.singleShot(0, self._prompt_affinity_install)
    
    def _prompt_affinity_install(self):
        """Prompt user to install an Affinity application"""
        reply = QMessageBox.question(
            self,
            "Install Affinity Application",
            "Setup is complete!\n\nWould you like to install an Affinity application now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Show a dialog to select which app
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Affinity Application")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            label = QLabel("Which Affinity application would you like to install?")
            layout.addWidget(label)
            
            button_group = QButtonGroup()
            apps = [
                ("Add", "Affinity (Unified)"),
                ("Photo", "Affinity Photo"),
                ("Designer", "Affinity Designer"),
                ("Publisher", "Affinity Publisher")
            ]
            
            radio_buttons = {}
            for idx, (app_code, app_name) in enumerate(apps):
                radio = QRadioButton(app_name)
                if app_code == "Add":
                    radio.setChecked(True)
                button_group.addButton(radio, idx)
                radio_buttons[idx] = app_code
                layout.addWidget(radio)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                checked_id = button_group.checkedId()
                if checked_id >= 0 and checked_id in radio_buttons:
                    app_code = radio_buttons[checked_id]
                    self.install_application(app_code)
    
    def check_dependencies(self):
        """Check and install dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Dependency Verification", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Show unsupported warning
        if self.distro in ["ubuntu", "linuxmint", "pop", "zorin"]:
            self.show_unsupported_warning()
        
        missing = []
        deps = ["wine", "winetricks", "wget", "curl", "7z", "tar", "jq"]
        
        for dep in deps:
            if self.check_command(dep):
                self.log(f"{dep} is installed", "success")
            else:
                self.log(f"{dep} is not installed", "error")
                missing.append(dep)
        
        # Check zstd
        if not (self.check_command("unzstd") or self.check_command("zstd")):
            self.log("zstd or unzstd is not installed", "error")
            missing.append("zstd")
        else:
            self.log("zstd support is available", "success")
        
        # Handle unsupported distributions
        if self.distro in ["ubuntu", "linuxmint", "pop", "zorin"]:
            if missing:
                self.log("\nMissing dependencies detected.", "error")
                self.log("This script will NOT auto-install for unsupported distributions.", "error")
                return False
            else:
                self.log("\nAll dependencies installed, but you are on an unsupported distribution.", "warning")
                self.log("No support will be provided if issues arise.", "warning")
        
        # Install missing dependencies
        if missing:
            self.log(f"\nInstalling missing dependencies: {', '.join(missing)}", "info")
            if not self.install_dependencies():
                return False
        
        self.log("\n✓ All required dependencies are installed!", "success")
        return True
    
    def show_unsupported_warning(self):
        """Display unsupported distribution warning"""
        self.log("\n" + "="*80, "warning")
        self.log("⚠️  WARNING: UNSUPPORTED DISTRIBUTION", "error")
        self.log("="*80, "warning")
        self.log(f"\nYOU ARE ON YOUR OWN!", "error")
        self.log(f"\nThe distribution ({self.distro}) is OUT OF DATE", "warning")
        self.log("and the script will NOT be built around it.", "warning")
        self.log("\nFor a modern, stable Linux experience, please consider:", "info")
        self.log("  • PikaOS 4", "success")
        self.log("  • CachyOS", "success")
        self.log("  • Nobara", "success")
        self.log("="*80 + "\n", "warning")
    
    def install_dependencies(self):
        """Install dependencies based on distribution"""
        if self.distro == "pikaos":
            return self.install_pikaos_dependencies()
        
        commands = {
            "arch": ["sudo", "pacman", "-S", "--needed", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"],
            "cachyos": ["sudo", "pacman", "-S", "--needed", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"],
            "fedora": ["sudo", "dnf", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "p7zip-plugins", "tar", "jq", "zstd"],
            "nobara": ["sudo", "dnf", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "p7zip-plugins", "tar", "jq", "zstd"],
            "opensuse-tumbleweed": ["sudo", "zypper", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"],
            "opensuse-leap": ["sudo", "zypper", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"]
        }
        
        if self.distro in commands:
            self.log(f"Installing dependencies for {self.distro}...", "info")
            success, stdout, stderr = self.run_command(commands[self.distro])
            if success:
                self.log("Dependencies installed successfully", "success")
                return True
            else:
                self.log(f"Failed to install dependencies: {stderr}", "error")
                return False
        
        self.log(f"Unsupported distribution: {self.distro}", "error")
        return False
    
    def install_pikaos_dependencies(self):
        """Install PikaOS dependencies with WineHQ staging"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("PikaOS Special Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log("PikaOS's built-in Wine has compatibility issues.", "warning")
        self.log("Setting up WineHQ staging from Debian...\n", "info")
        
        # Create keyrings directory
        self.log("Creating APT keyrings directory...", "info")
        success, _, _ = self.run_command(["sudo", "mkdir", "-pm755", "/etc/apt/keyrings"])
        if not success:
            self.log("Failed to create keyrings directory", "error")
            return False
        
        # Add GPG key
        self.log("Adding WineHQ GPG key...", "info")
        success, stdout, _ = self.run_command(["wget", "-O", "-", "https://dl.winehq.org/wine-builds/winehq.key"])
        if success:
            gpg_proc = subprocess.Popen(
                ["sudo", "gpg", "--dearmor", "-o", "/etc/apt/keyrings/winehq-archive.key", "-"],
                stdin=subprocess.PIPE
            )
            gpg_proc.communicate(input=stdout.encode())
            if gpg_proc.returncode == 0:
                self.log("WineHQ GPG key added", "success")
            else:
                self.log("Failed to add GPG key", "error")
                return False
        else:
            self.log("Failed to download GPG key", "error")
            return False
        
        # Add i386 architecture
        self.log("Adding i386 architecture...", "info")
        success, _, _ = self.run_command(["sudo", "dpkg", "--add-architecture", "i386"])
        if not success:
            self.log("Failed to add i386 architecture", "error")
            return False
        
        # Add repository
        self.log("Adding WineHQ repository...", "info")
        success, _, _ = self.run_command([
            "sudo", "wget", "-NP", "/etc/apt/sources.list.d/",
            "https://dl.winehq.org/wine-builds/debian/dists/forky/winehq-forky.sources"
        ])
        if not success:
            self.log("Failed to add repository", "error")
            return False
        
        # Update package lists
        self.log("Updating package lists...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "update"])
        if not success:
            self.log("Failed to update package lists", "error")
            return False
        
        # Install WineHQ staging
        self.log("Installing WineHQ staging...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "install", "--install-recommends", "-y", "winehq-staging"])
        if not success:
            self.log("Failed to install WineHQ staging", "error")
            return False
        
        # Install remaining dependencies
        self.log("Installing remaining dependencies...", "info")
        success, _, _ = self.run_command([
            "sudo", "apt", "install", "-y", "winetricks", "wget", "curl", "p7zip-full", "tar", "jq", "zstd"
        ])
        if not success:
            self.log("Failed to install remaining dependencies", "error")
            return False
        
        self.log("All dependencies installed for PikaOS", "success")
        return True
    
    def setup_wine(self):
        """Setup Wine environment"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Wine Binary Setup", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Stop Wine processes
        self.log("Stopping Wine processes...", "info")
        self.run_command(["wineserver", "-k"], check=False)
        
        # Create directory
        Path(self.directory).mkdir(parents=True, exist_ok=True)
        self.log("Installation directory created", "success")
        
        # Download Wine binary
        wine_url = "https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
        wine_file = Path(self.directory) / "ElementalWarriorWine-x86_64.tar.gz"
        
        self.log("Downloading Wine binary...", "info")
        if not self.download_file(wine_url, str(wine_file), "Wine binaries"):
            self.log("Failed to download Wine binary", "error")
            return False
        
        # Extract Wine
        self.log("Extracting Wine binary...", "info")
        try:
            with tarfile.open(wine_file, "r:gz") as tar:
                tar.extractall(self.directory, filter='data')
            wine_file.unlink()
            self.log("Wine binary extracted", "success")
        except Exception as e:
            self.log(f"Failed to extract Wine: {e}", "error")
            return False
        
        # Find and link Wine directory
        wine_dir = next(Path(self.directory).glob("ElementalWarriorWine*"), None)
        if wine_dir and wine_dir != Path(self.directory) / "ElementalWarriorWine":
            target = Path(self.directory) / "ElementalWarriorWine"
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(wine_dir)
            self.log("Wine symlink created", "success")
        
        # Verify Wine binary
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine binary not found", "error")
            return False
        
        self.log("Wine binary verified", "success")
        
        # Download icons
        self.log("\nSetting up application icons...", "info")
        icons_dir = Path.home() / ".local" / "share" / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        icons = [
            ("https://github.com/user-attachments/assets/c7b70ee5-58e3-46c6-b385-7c3d02749664",
             icons_dir / "AffinityPhoto.svg", "Photo icon"),
            ("https://github.com/user-attachments/assets/8ea7f748-c455-4ee8-9a94-775de40dbbf3",
             icons_dir / "AffinityDesigner.svg", "Designer icon"),
            ("https://github.com/user-attachments/assets/96ae06f8-470b-451f-ba29-835324b5b552",
             icons_dir / "AffinityPublisher.svg", "Publisher icon"),
            ("https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-V3.svg",
             icons_dir / "Affinity.svg", "Affinity V3 icon")
        ]
        
        for url, path, desc in icons:
            if not self.download_file(url, str(path), desc):
                self.log(f"Warning: {desc} download failed, but continuing...", "warning")
        
        # Setup WinMetadata
        self.setup_winmetadata()
        
        # Setup vkd3d-proton
        self.setup_vkd3d()
        
        # Configure Wine
        self.configure_wine()
        
        self.setup_complete = True
        self.log("\n✓ Wine setup completed!", "success")
    
    def setup_winmetadata(self):
        """Download and extract WinMetadata"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Windows Metadata Installation", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        winmetadata_zip = Path(self.directory) / "Winmetadata.zip"
        system32_dir = Path(self.directory) / "drive_c" / "windows" / "system32"
        system32_dir.mkdir(parents=True, exist_ok=True)
        
        self.log("Downloading Windows metadata...", "info")
        if not self.download_file(
            "https://archive.org/download/win-metadata/WinMetadata.zip",
            str(winmetadata_zip),
            "WinMetadata"
        ):
            self.log("Failed to download WinMetadata", "warning")
            return
        
        # Extract WinMetadata
        self.log("Extracting Windows metadata...", "info")
        try:
            if self.check_command("7z"):
                success, _, _ = self.run_command([
                    "7z", "x", str(winmetadata_zip), f"-o{system32_dir}", "-y"
                ])
                if success:
                    self.log("WinMetadata extracted using 7z", "success")
                    return
            elif self.check_command("unzip"):
                with zipfile.ZipFile(winmetadata_zip, 'r') as zip_ref:
                    zip_ref.extractall(system32_dir)
                self.log("WinMetadata extracted using unzip", "success")
                return
            else:
                self.log("Neither 7z nor unzip available", "error")
        except Exception as e:
            self.log(f"Extraction failed: {e}", "error")
    
    def reinstall_winmetadata(self):
        """Remove old WinMetadata folder and reinstall fresh"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Reinstall WinMetadata", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please setup Wine environment first.", "error")
            QMessageBox.warning(
                self,
                "Wine Not Ready",
                "Wine setup must complete before reinstalling WinMetadata.\n"
                "Please setup Wine environment first."
            )
            return
        
        threading.Thread(target=self._reinstall_winmetadata_thread, daemon=True).start()
    
    def _reinstall_winmetadata_thread(self):
        """Reinstall WinMetadata in background thread"""
        # Kill Wine processes
        self.log("Stopping Wine processes...", "info")
        self.run_command(["wineserver", "-k"], check=False)
        time.sleep(2)
        
        system32_dir = Path(self.directory) / "drive_c" / "windows" / "system32"
        winmetadata_dir = system32_dir / "WinMetadata"
        
        # Remove existing WinMetadata folder
        if winmetadata_dir.exists():
            self.log("Removing existing WinMetadata folder...", "info")
            try:
                shutil.rmtree(winmetadata_dir)
                self.log("Old WinMetadata folder removed", "success")
            except Exception as e:
                self.log(f"Warning: Could not fully remove old folder: {e}", "warning")
        
        # Also remove the zip file to force re-download
        winmetadata_zip = Path(self.directory) / "Winmetadata.zip"
        if winmetadata_zip.exists():
            self.log("Removing cached WinMetadata.zip to force fresh download...", "info")
            try:
                winmetadata_zip.unlink()
                self.log("Cached zip file removed", "success")
            except Exception as e:
                self.log(f"Warning: Could not remove cached zip: {e}", "warning")
        
        # Ensure system32 directory exists
        system32_dir.mkdir(parents=True, exist_ok=True)
        
        # Reinstall WinMetadata
        self.log("Installing fresh WinMetadata...", "info")
        self.setup_winmetadata()
        
        self.log("\n✓ WinMetadata reinstallation completed!", "success")
    
    def setup_vkd3d(self):
        """Setup vkd3d-proton for OpenCL"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("OpenCL Support Setup", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        vkd3d_url = "https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst"
        vkd3d_file = Path(self.directory) / "vkd3d-proton-2.14.1.tar.zst"
        vkd3d_temp = Path(self.directory) / "vkd3d_dlls"
        vkd3d_temp.mkdir(exist_ok=True)
        
        self.log("Downloading vkd3d-proton...", "info")
        if not self.download_file(vkd3d_url, str(vkd3d_file), "vkd3d-proton"):
            self.log("Failed to download vkd3d-proton", "error")
            return
        
        # Extract vkd3d-proton
        self.log("Extracting vkd3d-proton...", "info")
        if self.check_command("unzstd"):
            tar_file = Path(self.directory) / "vkd3d-proton.tar"
            success, _, _ = self.run_command(["unzstd", "-f", str(vkd3d_file), "-o", str(tar_file)])
            if success:
                with tarfile.open(tar_file, "r") as tar:
                    tar.extractall(self.directory, filter='data')
                tar_file.unlink()
                self.log("vkd3d-proton extracted", "success")
        
        vkd3d_file.unlink()
        
        # Copy DLLs
        vkd3d_dir = next(Path(self.directory).glob("vkd3d-proton-*"), None)
        if vkd3d_dir:
            wine_lib_dir = Path(self.directory) / "ElementalWarriorWine" / "lib" / "wine" / "vkd3d-proton" / "x86_64-windows"
            wine_lib_dir.mkdir(parents=True, exist_ok=True)
            
            for dll in ["d3d12.dll", "d3d12core.dll"]:
                for source_dir in [vkd3d_dir / "x64", vkd3d_dir]:
                    src = source_dir / dll
                    if src.exists():
                        shutil.copy2(src, vkd3d_temp / dll)
                        shutil.copy2(src, wine_lib_dir / dll)
                        self.log(f"Copied {dll}", "success")
                        break
            
            shutil.rmtree(vkd3d_dir)
            self.log("vkd3d-proton setup completed", "success")
    
    def configure_wine(self):
        """Configure Wine with winetricks"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Wine Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        components = [
            "dotnet35", "dotnet48", "corefonts", "vcrun2022", 
            "msxml3", "msxml6", "renderer=vulkan"
        ]
        
        self.log("Installing Wine components (this may take several minutes)...", "info")
        for component in components:
            self.log(f"Installing {component}...", "info")
            self.run_command(
                ["winetricks", "--unattended", "--force", "--no-isolate", "--optout", component],
                check=False,
                env=env
            )
        
        # Set Windows version to 11
        self.log("Setting Windows version to 11...", "info")
        self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
        
        # Apply dark theme
        self.log("Applying Wine dark theme...", "info")
        theme_file = Path(self.directory) / "wine-dark-theme.reg"
        if self.download_file(
            "https://raw.githubusercontent.com/seapear/AffinityOnLinux/refs/heads/main/Auxiliary/Other/wine-dark-theme.reg",
            str(theme_file),
            "dark theme"
        ):
            regedit = Path(self.directory) / "ElementalWarriorWine" / "bin" / "regedit"
            self.run_command([str(regedit), str(theme_file)], check=False, env=env)
            theme_file.unlink()
        
        self.log("Wine configuration completed", "success")
    
    def show_main_menu(self):
        """Display main application menu"""
        self.log("\n✓ Setup complete! Select an application to install:", "success")
        self.update_progress(1.0)
    
    def install_system_dependencies(self):
        """Install system dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Installing System Dependencies", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        threading.Thread(target=self._install_system_deps, daemon=True).start()
    
    def _install_system_deps(self):
        """Install system dependencies in thread"""
        if self.distro == "pikaos":
            self.log("Using PikaOS dependency installation...", "info")
            success = self.install_pikaos_dependencies()
            self.log("System dependencies installation completed" if success else "System dependencies installation failed", "success" if success else "error")
            return
        
        if not self.distro:
            self.detect_distro()
        
        self.log(f"Installing dependencies for {self.distro}...", "info")
        success = self.install_dependencies()
        self.log("System dependencies installation completed" if success else "System dependencies installation failed", "success" if success else "error")
    
    def install_winetricks_dependencies(self):
        """Install winetricks dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Installing Winetricks Dependencies", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please wait for Wine setup to complete.", "error")
            QMessageBox.warning(self, "Wine Not Ready", "Wine setup must complete before installing winetricks dependencies.")
            return
        
        threading.Thread(target=self._install_winetricks_deps, daemon=True).start()
    
    def _install_winetricks_deps(self):
        """Install winetricks dependencies in thread"""
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        components = [
            ("dotnet35", ".NET Framework 3.5"),
            ("dotnet48", ".NET Framework 4.8"),
            ("corefonts", "Windows Core Fonts"),
            ("vcrun2022", "Visual C++ Redistributables 2022"),
            ("msxml3", "MSXML 3.0"),
            ("msxml6", "MSXML 6.0"),
            ("renderer=vulkan", "Vulkan Renderer")
        ]
        
        self.log("Installing Wine components (this may take several minutes)...", "info")
        
        for component, description in components:
            self.log(f"Installing {description} ({component})...", "info")
            success, stdout, stderr = self.run_command(
                ["winetricks", "--unattended", "--force", "--no-isolate", "--optout", component],
                check=False,
                env=env
            )
            
            if success:
                self.log(f"✓ {description} installed", "success")
            else:
                # If installation failed, try once more with force
                self.log(f"⚠ {description} installation failed, retrying...", "warning")
                time.sleep(2)  # Brief pause before retry
                
                retry_success, retry_stdout, retry_stderr = self.run_command(
                    ["winetricks", "--unattended", "--force", "--no-isolate", "--optout", component],
                    check=False,
                    env=env
                )
                
                if retry_success:
                    self.log(f"✓ {description} installed successfully on retry", "success")
                else:
                    # Check if it might already be installed (common error pattern)
                    error_msg = (retry_stderr or "").lower()
                    if "already installed" in error_msg or "already exists" in error_msg:
                        self.log(f"✓ {description} appears to already be installed", "success")
                    else:
                        self.log(f"✗ {description} installation failed after retry. You may need to install manually.", "error")
                        self.log(f"  Error details: {retry_stderr[:200] if retry_stderr else 'Unknown error'}", "error")
        
        # Set Windows version to 11
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        self.log("Setting Windows version to 11...", "info")
        self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
        
        # Apply dark theme
        self.log("Applying Wine dark theme...", "info")
        theme_file = Path(self.directory) / "wine-dark-theme.reg"
        if self.download_file(
            "https://raw.githubusercontent.com/seapear/AffinityOnLinux/refs/heads/main/Auxiliary/Other/wine-dark-theme.reg",
            str(theme_file),
            "dark theme"
        ):
            regedit = Path(self.directory) / "ElementalWarriorWine" / "bin" / "regedit"
            self.run_command([str(regedit), str(theme_file)], check=False, env=env)
            theme_file.unlink()
            self.log("Dark theme applied", "success")
        
        self.log("\n✓ Winetricks dependencies installation completed!", "success")
    
    def install_from_file(self):
        """Install from file manager - custom .exe file"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Custom Installer from File Manager", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please wait for Wine setup to complete.", "error")
            QMessageBox.warning(
                self,
                "Wine Not Ready",
                "Wine setup must complete before installing applications.\n"
                "Please wait for the initialization to finish."
            )
            return
        
        # Open file dialog to select .exe
        self.log("Please select the installer .exe file...", "info")
        installer_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Installer (.exe)",
            "",
            "Executable files (*.exe);;All files (*.*)"
        )
        
        if not installer_path:
            self.log("Installation cancelled.", "warning")
            return
        
        # Ask for application name
        app_name, ok = QMessageBox.getText(
            self,
            "Application Name",
            "Enter the name for this application:\n(e.g., 'MyApp', 'CustomSoftware')"
        )
        
        if not ok or not app_name:
            app_name = "CustomApp"
        
        # Start installation
        threading.Thread(
            target=self.run_custom_installation,
            args=(installer_path, app_name),
            daemon=True
        ).start()
    
    def run_custom_installation(self, installer_path, app_name):
        """Run custom installation process"""
        try:
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer
            installer_file = Path(self.directory) / Path(installer_path).name
            shutil.copy2(installer_path, installer_file)
            self.log("Installer copied to Wine prefix", "success")
            
            # Set Windows version
            wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
            
            # Run installer
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            env["WINEDEBUG"] = "-all"
            self.log("Launching installer with custom Wine...", "info")
            self.log("Follow the installation wizard in the window that opens.", "info")
            self.log("Click 'No' if you encounter any errors.", "warning")
            
            self.run_command([str(wine), str(installer_file)], check=False, env=env, capture=False)
            
            # Wait for completion
            time.sleep(3)
            
            # Clean up installer
            if installer_file.exists():
                installer_file.unlink()
            self.log("Installer file removed", "success")
            
            # Restore WinMetadata
            self.restore_winmetadata()
            
            # Ask if user wants to create desktop entry (this needs to be called from main thread)
            # Use QTimer to ensure it runs on main thread
            QTimer.singleShot(0, lambda path=installer_path, name=app_name: self.create_custom_desktop_entry(path, name))
            
            self.log(f"\n✓ {app_name} installation completed!", "success")
            
            self.show_message(
                "Installation Complete",
                f"{app_name} has been successfully installed using the custom Wine!\n\n"
                "You can launch it from your application menu if a desktop entry was created.",
                "info"
            )
        except Exception as e:
            self.log(f"Installation error: {e}", "error")
            self.show_message("Installation Error", f"An error occurred:\n{e}", "error")
    
    def create_custom_desktop_entry(self, installer_path, app_name):
        """Create desktop entry for custom installed app"""
        reply = QMessageBox.question(
            self,
            "Create Desktop Entry",
            f"Would you like to create a desktop entry for '{app_name}'?\n\n"
            "You'll need to provide the executable path.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Ask for executable path
        exe_path, ok = QMessageBox.getText(
            self,
            "Executable Path",
            f"Enter the full path to the {app_name} executable:\n\n"
            "Example: C:\\Program Files\\MyApp\\MyApp.exe"
        )
        
        if not ok or not exe_path:
            self.log("Desktop entry creation cancelled.", "warning")
            return
        
        # Ask for icon path (optional)
        icon_path, ok = QMessageBox.getText(
            self,
            "Icon Path (Optional)",
            "Enter the path to an icon file (optional):\n\n"
            "Leave blank to use default icon."
        )
        
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / f"{app_name.replace(' ', '')}.desktop"
        
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        
        with open(desktop_file, "w") as f:
            f.write("[Desktop Entry]\n")
            f.write(f"Name={app_name}\n")
            f.write(f"Comment={app_name} installed via Affinity Linux Installer\n")
            if icon_path:
                f.write(f"Icon={icon_path}\n")
            f.write(f"Path={self.directory}\n")
            f.write(f'Exec=env WINEPREFIX={self.directory} {wine} "{exe_path}"\n')
            f.write("Terminal=false\n")
            f.write("Type=Application\n")
            f.write("Categories=Application;\n")
            f.write("StartupNotify=true\n")
        
        self.log(f"Desktop entry created: {desktop_file}", "success")
    
    def update_application(self, app_name):
        """Update Affinity application - simple installer that assumes everything is set up"""
        app_names = {
            "Add": "Affinity (Unified)",
            "Photo": "Affinity Photo",
            "Designer": "Affinity Designer",
            "Publisher": "Affinity Publisher"
        }
        
        display_name = app_names.get(app_name, app_name)
        
        self.log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log(f"Update {display_name}", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Wine is set up
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        # Ask for installer file
        self.log(f"Please select the {display_name} installer (.exe)...", "info")
        
        installer_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {display_name} Installer",
            "",
            "Executable files (*.exe);;All files (*.*)"
        )
        
        if not installer_path:
            self.log("Update cancelled.", "warning")
            return
        
        # Start update in thread
        threading.Thread(
            target=self.run_update,
            args=(display_name, installer_path),
            daemon=True
        ).start()
    
    def run_update(self, display_name, installer_path):
        """Run the update process - simple installer without desktop entries or deps"""
        try:
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer to Wine prefix
            installer_file = Path(self.directory) / Path(installer_path).name
            shutil.copy2(installer_path, installer_file)
            self.log("Installer copied to Wine prefix", "success")
            
            # Set up environment
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            env["WINEDEBUG"] = "-all"
            
            # Run installer with custom Wine
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            self.log("Launching installer...", "info")
            self.log("Follow the installation wizard in the window that opens.", "info")
            self.log("This will update the application without creating desktop entries.", "info")
            
            self.run_command([str(wine), str(installer_file)], check=False, env=env, capture=False)
            
            # Wait a moment for installer to complete
            time.sleep(3)
            
            # Clean up installer
            if installer_file.exists():
                installer_file.unlink()
                self.log("Installer file removed", "success")
            
            self.log(f"\n✓ {display_name} update completed!", "success")
            self.log("The application has been updated. Use your existing desktop entry to launch it.", "info")
            
            self.show_message(
                "Update Complete",
                f"{display_name} has been successfully updated!\n\n"
                "Use your existing desktop entry to launch the application.",
                "info"
            )
        except Exception as e:
            self.log(f"Update error: {e}", "error")
            self.show_message("Update Error", f"An error occurred:\n{e}", "error")
    
    def run_installation(self, app_name, installer_path):
        """Run the installation process"""
        try:
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer
            installer_file = Path(self.directory) / Path(installer_path).name
            shutil.copy2(installer_path, installer_file)
            self.log("Installer copied", "success")
            
            # Set Windows version
            wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
            
            # Run installer
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            env["WINEDEBUG"] = "-all"
            self.log("Launching installer...", "info")
            self.log("Follow the installation wizard in the window that opens.", "info")
            self.log("Click 'No' if you encounter any errors.", "warning")
            
            self.run_command([str(wine), str(installer_file)], check=False, env=env, capture=False)
            
            # Wait for completion
            time.sleep(3)
            
            # Clean up installer
            installer_file.unlink()
            self.log("Installer file removed", "success")
            
            # Restore WinMetadata
            self.restore_winmetadata()
            
            # Configure OpenCL
            self.configure_opencl(app_name)
            
            # Create desktop entry
            self.create_desktop_entry(app_name)
            
            self.log(f"\n✓ {app_name} installation completed!", "success")
            self.log("You can now launch it from your application menu.", "info")
            
            self.show_message(
                "Installation Complete",
                f"{app_name} has been successfully installed!\n\n"
                "You can launch it from your application menu.",
                "info"
            )
        except Exception as e:
            self.log(f"Installation error: {e}", "error")
            self.show_message("Installation Error", f"An error occurred:\n{e}", "error")
    
    def restore_winmetadata(self):
        """Restore WinMetadata after installation"""
        self.log("Restoring Windows metadata files...", "info")
        
        # Kill Wine processes
        self.run_command(["wineserver", "-k"], check=False)
        time.sleep(2)
        
        winmetadata_zip = Path(self.directory) / "Winmetadata.zip"
        system32_dir = Path(self.directory) / "drive_c" / "windows" / "system32"
        
        if winmetadata_zip.exists():
            # Re-extract
            try:
                if self.check_command("7z"):
                    self.run_command([
                        "7z", "x", str(winmetadata_zip),
                        f"-o{system32_dir}", "-y"
                    ], check=False)
                elif self.check_command("unzip"):
                    with zipfile.ZipFile(winmetadata_zip, 'r') as zip_ref:
                        zip_ref.extractall(system32_dir)
                self.log("WinMetadata restored", "success")
            except Exception as e:
                self.log(f"Failed to restore WinMetadata: {e}", "warning")
        else:
            # Re-download if not cached
            self.log("WinMetadata.zip not found, downloading...", "info")
            self.setup_winmetadata()
    
    def configure_opencl(self, app_name):
        """Configure OpenCL for application"""
        app_dirs = {
            "Photo": "Photo 2",
            "Designer": "Designer 2",
            "Publisher": "Publisher 2",
            "Add": "Affinity"
        }
        
        app_dir_name = app_dirs.get(app_name, "Affinity")
        app_dir = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / app_dir_name
        
        if not app_dir.exists():
            self.log(f"Application directory not found: {app_dir}", "warning")
            return
        
        wine_lib_dir = Path(self.directory) / "ElementalWarriorWine" / "lib" / "wine" / "vkd3d-proton" / "x86_64-windows"
        vkd3d_temp = Path(self.directory) / "vkd3d_dlls"
        
        dlls_copied = 0
        for dll in ["d3d12.dll", "d3d12core.dll"]:
            for source in [vkd3d_temp / dll, wine_lib_dir / dll]:
                if source.exists():
                    shutil.copy2(source, app_dir / dll)
                    self.log(f"Copied {dll}", "success")
                    dlls_copied += 1
                    break
        
        # Configure DLL overrides
        reg_file = Path(self.directory) / "dll_overrides.reg"
        with open(reg_file, "w") as f:
            f.write("REGEDIT4\n")
            f.write("[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]\n")
            f.write('"d3d12"="native"\n')
            f.write('"d3d12core"="native"\n')
        
        regedit = Path(self.directory) / "ElementalWarriorWine" / "bin" / "regedit"
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        self.run_command([str(regedit), str(reg_file)], check=False, env=env)
        reg_file.unlink()
        
        if dlls_copied > 0:
            self.log("OpenCL support configured", "success")
    
    def create_desktop_entry(self, app_name):
        """Create desktop entry for application"""
        app_names = {
            "Photo": ("Photo", "Photo.exe", "Photo 2", "AffinityPhoto.svg"),
            "Designer": ("Designer", "Designer.exe", "Designer 2", "AffinityDesigner.svg"),
            "Publisher": ("Publisher", "Publisher.exe", "Publisher 2", "AffinityPublisher.svg"),
            "Add": ("Affinity", "Affinity.exe", "Affinity", "Affinity.svg")
        }
        
        name, exe, dir_name, icon = app_names.get(app_name, ("Affinity", "Affinity.exe", "Affinity", "Affinity.svg"))
        
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / f"Affinity{name}.desktop"
        if app_name == "Add":
            desktop_file = desktop_dir / "Affinity.desktop"
        
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        app_path = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / dir_name / exe
        icon_path = Path.home() / ".local" / "share" / "icons" / icon
        
        with open(desktop_file, "w") as f:
            f.write("[Desktop Entry]\n")
            f.write(f"Name=Affinity {name}\n")
            f.write(f"Comment=A powerful {name.lower()} software.\n")
            f.write(f"Icon={icon_path}\n")
            f.write(f"Path={self.directory}\n")
            f.write(f'Exec=env WINEPREFIX={self.directory} {wine} "{app_path}"\n')
            f.write("Terminal=false\n")
            f.write("Type=Application\n")
            f.write("Categories=Graphics;\n")
            f.write("StartupNotify=true\n")
            if app_name == "Add":
                f.write("StartupWMClass=affinity.exe\n")
            else:
                f.write(f"StartupWMClass={name.lower()}.exe\n")
        
        # Remove Wine's default entry
        wine_entry = desktop_dir / "wine" / "Programs" / f"Affinity {name} 2.desktop"
        if wine_entry.exists():
            wine_entry.unlink()
        
        if app_name == "Add":
            wine_entry = desktop_dir / "wine" / "Programs" / "Affinity.desktop"
            if wine_entry.exists():
                wine_entry.unlink()
        
        # Create desktop shortcut
        desktop_shortcut = Path.home() / "Desktop" / desktop_file.name
        if desktop_shortcut.parent.exists():
            shutil.copy2(desktop_file, desktop_shortcut)
        
        self.log(f"Desktop entry created: {desktop_file}", "success")
        self.log("Desktop shortcut created", "success")
    
    def open_winecfg(self):
        """Open Wine Configuration tool using custom Wine"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Opening Wine Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        if not wine_cfg.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        self.log(f"Opening winecfg using: {wine_cfg}", "info")
        self.log("The Wine Configuration window should open now.", "info")
        
        # Run winecfg in background (non-blocking)
        threading.Thread(
            target=lambda: self.run_command([str(wine_cfg)], check=False, capture=False, env=env),
            daemon=True
        ).start()
        
        self.log("✓ Wine Configuration opened", "success")
    
    def set_windows11_renderer(self):
        """Set Windows 11 and configure renderer (OpenGL or Vulkan)"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Windows 11 + Renderer Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        if not wine_cfg.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        # Ask user to choose renderer
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Renderer")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Choose a renderer for troubleshooting:")
        layout.addWidget(label)
        
        button_group = QButtonGroup()
        vulkan_radio = QRadioButton("Vulkan (Recommended - OpenCL support)")
        vulkan_radio.setChecked(True)
        opengl_radio = QRadioButton("OpenGL (Alternative)")
        gdi_radio = QRadioButton("GDI (Fallback)")
        
        button_group.addButton(vulkan_radio, 0)
        button_group.addButton(opengl_radio, 1)
        button_group.addButton(gdi_radio, 2)
        
        layout.addWidget(vulkan_radio)
        layout.addWidget(opengl_radio)
        layout.addWidget(gdi_radio)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self.log("Renderer configuration cancelled", "warning")
            return
        
        # Determine selected renderer
        renderer_map = {
            0: ("vulkan", "Vulkan"),
            1: ("opengl", "OpenGL"),
            2: ("gdi", "GDI")
        }
        
        selected_id = button_group.checkedId()
        renderer_value, renderer_name = renderer_map.get(selected_id, ("vulkan", "Vulkan"))
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        # Set Windows version to 11
        self.log("Setting Windows version to 11...", "info")
        success, _, _ = self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
        if success:
            self.log("✓ Windows version set to 11", "success")
        else:
            self.log("⚠ Warning: Failed to set Windows version", "warning")
        
        # Configure renderer using winetricks
        self.log(f"Configuring {renderer_name} renderer...", "info")
        success, stdout, stderr = self.run_command(
            ["winetricks", "--unattended", "--force", "--no-isolate", "--optout", f"renderer={renderer_value}"],
            check=False,
            env=env
        )
        
        if success:
            self.log(f"✓ {renderer_name} renderer configured successfully", "success")
        else:
            error_msg = (stderr or "").lower()
            if "already installed" in error_msg or "already exists" in error_msg:
                self.log(f"✓ {renderer_name} renderer is already configured", "success")
            else:
                self.log(f"⚠ Warning: {renderer_name} renderer configuration may have failed", "warning")
                self.log(f"  Error: {stderr[:200] if stderr else 'Unknown error'}", "error")
        
        self.log("\n✓ Windows 11 and renderer configuration completed", "success")
    
    def show_thanks(self):
        """Show special thanks window"""
        thanks = QMessageBox(self)
        thanks.setWindowTitle("Special Thanks")
        thanks.setText("Special Thanks\n\n"
                      "Ardishco (github.com/raidenovich)\n"
                      "Deviaze\n"
                      "Kemal\n"
                      "Jacazimbo <3\n"
                      "Kharoon\n"
                      "Jediclank134")
        thanks.setStandardButtons(QMessageBox.StandardButton.Ok)
        thanks.exec()


def main():
    """Main entry point"""
    if platform.system() != "Linux":
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Unsupported Platform",
            "This installer is designed for Linux systems only."
        )
        return
    
    app = QApplication(sys.argv)
    window = AffinityInstallerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
