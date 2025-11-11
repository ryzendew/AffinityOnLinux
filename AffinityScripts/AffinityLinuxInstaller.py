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
import re
from pathlib import Path
import time
import signal
import shlex
# Function to detect Linux distribution
def detect_distro_for_install():
    """Detect distribution for package installation"""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
        for line in content.split("\n"):
            if line.startswith("ID="):
                distro = line.split("=", 1)[1].strip().strip('"').lower()
                # Normalize "pika" to "pikaos" if detected
                if distro == "pika":
                    distro = "pikaos"
                return distro
    except (IOError, FileNotFoundError):
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
        if distro in ["arch", "cachyos", "manjaro", "endeavouros", "xerolinux"]:
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
        QButtonGroup, QRadioButton, QInputDialog, QSlider, QLineEdit
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QShortcut, QKeySequence, QWheelEvent, QPainter, QPen
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
                QButtonGroup, QRadioButton, QInputDialog, QSlider, QLineEdit
            )
            from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
            from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QShortcut, QKeySequence, QWheelEvent
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
    print("  Arch/CachyOS/EndeavourOS/XeroLinux: sudo pacman -S python-pyqt6")
    print("  Fedora/Nobara: sudo dnf install python3-pyqt6")
    print("  Debian/Ubuntu/Mint/Pop/Zorin/PikaOS: sudo apt install python3-pyqt6")
    print("  openSUSE: sudo zypper install python313-PyQt6")
    sys.exit(1)


class ZoomableTextEdit(QTextEdit):
    """QTextEdit with Ctrl+Wheel zoom support"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_in_callback = None
        self.zoom_out_callback = None
    
    def set_zoom_callbacks(self, zoom_in, zoom_out):
        """Set callbacks for zoom in/out"""
        self.zoom_in_callback = zoom_in
        self.zoom_out_callback = zoom_out
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zoom (Ctrl+Wheel) or scroll"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
                if self.zoom_in_callback:
                    self.zoom_in_callback()
            elif delta < 0:
                self.zoomOut(1)
                if self.zoom_out_callback:
                    self.zoom_out_callback()
        else:
            # Normal scrolling
            super().wheelEvent(event)


class ProgressSpinner(QWidget):
    """A simple rotating spinner widget (indeterminate progress)."""
    def __init__(self, size=22, line_width=3, color=QColor('#8ff361'), parent=None):
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._on_timeout)
        self._size = size
        self._line_width = line_width
        self._color = color
        self.setFixedSize(self._size, self._size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def start(self):
        self._timer.start()
        self.update()

    def stop(self):
        self._timer.stop()
        self.update()

    def _on_timeout(self):
        self._angle = (self._angle - 30) % 360
        self.update()

    def paintEvent(self, event):  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(self._line_width, self._line_width, -self._line_width, -self._line_width)
        pen = QPen(self._color)
        pen.setWidth(self._line_width)
        painter.setPen(pen)
        # Draw an arc (270 degrees) rotating around
        start_angle = int(self._angle * 16)
        span_angle = int(270 * 16)
        painter.drawArc(rect, start_angle, span_angle)
        painter.end()

class AffinityInstallerGUI(QMainWindow):
    # Signals for thread-safe GUI updates
    log_signal = pyqtSignal(str, str)  # message, level
    progress_signal = pyqtSignal(float)  # value (0.0-1.0)
    progress_text_signal = pyqtSignal(str)  # progress text
    show_message_signal = pyqtSignal(str, str, str)  # title, message, type (info/error/warning)
    sudo_password_dialog_signal = pyqtSignal()  # Signal to request sudo password
    interactive_prompt_signal = pyqtSignal(str, str)  # prompt_text, default_response
    question_dialog_signal = pyqtSignal(str, str, list)  # title, message, buttons
    prompt_affinity_install_signal = pyqtSignal()  # Signal to prompt for Affinity installation
    install_application_signal = pyqtSignal(str)  # Signal to install an application
    show_spinner_signal = pyqtSignal(object)  # button -> show spinner
    hide_spinner_signal = pyqtSignal(object)  # button -> hide spinner
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Affinity Linux Installer")
        # Use a more reasonable initial size that fits smaller screens
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Variables
        self.distro = None
        self.distro_version = None
        self.directory = str(Path.home() / ".AffinityLinux")
        self.setup_complete = False
        self.installer_file = None
        self.update_buttons = {}  # Store references to update buttons
        self.log_font_size = 11  # Initial font size for log area
        self.operation_cancelled = False  # Flag to track if operation was cancelled
        self.current_operation = None  # Track current operation name
        self.operation_in_progress = False  # Track if an operation is running
        self.sudo_password = None  # Cached sudo password
        self.sudo_password_validated = False  # Whether password has been validated
        self.interactive_response = None  # Response to interactive prompts
        self.waiting_for_response = False  # Whether we're waiting for user response
        self.question_dialog_response = None  # Response from question dialogs
        self.waiting_for_question_response = False  # Whether waiting for question dialog response
        self.dark_mode = True  # Track current theme mode
        self.icon_buttons = []  # Store buttons with icons for theme updates
        # Cancellation helpers
        self.cancel_event = threading.Event()
        self._process_lock = threading.Lock()
        self._active_processes = set()
        # Spinner helpers
        self._button_spinner_map = {}
        self._last_clicked_button = None
        self._operation_button = None
        
        # Setup log file
        self.log_file_path = Path.home() / "AffinitySetup.log"
        self.log_file = None
        self._init_log_file()
        
        # Connect signals
        self.log_signal.connect(self._log_safe)
        self.progress_signal.connect(self._update_progress_safe)
        self.progress_text_signal.connect(self._update_progress_text_safe)
        self.show_message_signal.connect(self._show_message_safe)
        self.sudo_password_dialog_signal.connect(self._request_sudo_password_safe)
        self.interactive_prompt_signal.connect(self._request_interactive_response_safe)
        self.question_dialog_signal.connect(self._show_question_dialog_safe)
        self.prompt_affinity_install_signal.connect(self._prompt_affinity_install)
        self.install_application_signal.connect(self.install_application)
        self.show_spinner_signal.connect(self._show_spinner_safe)
        self.hide_spinner_signal.connect(self._hide_spinner_safe)
        
        # Load Affinity icon
        self.load_affinity_icon()
        
        # Setup UI
        self.create_ui()
        
        # Apply dark theme (default)
        self.apply_theme()
        
        # Setup zoom functionality
        self.setup_zoom()
        
        # Center window
        self.center_window()
        
        # Don't auto-start initialization - user will click button
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Affinity Linux Installer - Ready", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Ensure patcher files are available (silently)
        self.ensure_patcher_files(silent=True)
        
        self.log("System Detection:", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "info")
        
        # Check installation status and update button states
        self.check_installation_status()
        
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "info")
        self.log("Welcome! Please use the buttons on the right to get started.", "info")
        wine_path = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_path.exists():
            self.log("Click 'Setup Wine Environment' or 'One-Click Full Setup' to begin.", "info")
        else:
            self.log("Wine is set up. Use 'Update Affinity Applications' to install or update apps.", "info")
    
    def check_installation_status(self):
        """Check if Wine and Affinity applications are installed, and update button states"""
        # Check if Wine is set up
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        wine_exists = wine.exists()
        
        # Update system status indicator
        if hasattr(self, 'system_status_label'):
            if wine_exists:
                self.system_status_label.setStyleSheet("font-size: 14px; color: #4ec9b0; padding: 0 5px;")
                self.system_status_label.setToolTip("System Status: Ready - Wine is installed")
            else:
                self.system_status_label.setStyleSheet("font-size: 14px; color: #f48771; padding: 0 5px;")
                self.system_status_label.setToolTip("System Status: Not Ready - Wine needs to be installed")
        
        # Log Wine status
        if wine_exists:
            self.log("Wine: ✓ Installed (ElementalWarriorWine)", "success")
        else:
            self.log("Wine: ✗ Not installed", "error")
        
        # Check each Affinity application
        app_status = {}
        app_names_display = {
            "Add": "Affinity (Unified)",
            "Photo": "Affinity Photo",
            "Designer": "Affinity Designer",
            "Publisher": "Affinity Publisher"
        }
        app_dirs = {
            "Add": ("Affinity", "Affinity.exe"),
            "Photo": ("Photo 2", "Photo.exe"),
            "Designer": ("Designer 2", "Designer.exe"),
            "Publisher": ("Publisher 2", "Publisher.exe")
        }
        
        self.log("Affinity Applications:", "info")
        for app_name, (dir_name, exe_name) in app_dirs.items():
            app_path = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / dir_name / exe_name
            is_installed = app_path.exists()
            app_status[app_name] = is_installed
            
            display_name = app_names_display.get(app_name, app_name)
            if is_installed:
                self.log(f"  {display_name}: ✓ Installed", "success")
            else:
                self.log(f"  {display_name}: ✗ Not installed", "error")
            
            # Update button text to show installation status
            if app_name in self.update_buttons:
                btn = self.update_buttons[app_name]
                if is_installed:
                    # Add checkmark to button text if installed
                    current_text = btn.text()
                    if "✓" not in current_text:
                        btn.setText(current_text.split("✓")[0].strip() + " ✓")
                    btn.setEnabled(True)
        
        # Check dependencies
        self.log("System Dependencies:", "info")
        deps = ["wine", "winetricks", "wget", "curl", "7z", "tar", "jq"]
        deps_installed = True
        for dep in deps:
            if self.check_command(dep):
                self.log(f"  {dep}: ✓ Installed", "success")
            else:
                self.log(f"  {dep}: ✗ Not installed", "error")
                deps_installed = False
        
        # Check zstd
        if self.check_command("unzstd") or self.check_command("zstd"):
            self.log(f"  zstd: ✓ Installed", "success")
        else:
            self.log(f"  zstd: ✗ Not installed", "error")
            deps_installed = False
        
        # Check .NET SDK
        if self.check_dotnet_sdk():
            self.log(f"  .NET SDK: ✓ Installed", "success")
        else:
            self.log(f"  .NET SDK: ✗ Not installed", "error")
            # Don't set deps_installed = False since .NET SDK is optional (only needed for settings fix)
        
        # Check Winetricks Dependencies (only if Wine is set up)
        if wine_exists:
            self.log("Winetricks Dependencies:", "info")
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            
            # List of winetricks components to check
            winetricks_components = [
                ("dotnet35", ".NET Framework 3.5"),
                ("dotnet48", ".NET Framework 4.8"),
                ("corefonts", "Windows Core Fonts"),
                ("vcrun2022", "Visual C++ Redistributables 2022"),
                ("msxml3", "MSXML 3.0"),
                ("msxml6", "MSXML 6.0"),
            ]
            
            for component, description in winetricks_components:
                if self._check_winetricks_component(component, wine, env):
                    self.log(f"  {description}: ✓ Installed", "success")
                else:
                    self.log(f"  {description}: ✗ Not installed", "error")
            
            # Check Vulkan renderer
            try:
                success, stdout, _ = self.run_command(
                    [str(wine), "reg", "query", "HKEY_CURRENT_USER\\Software\\Wine\\Direct3D"],
                    check=False,
                    env=env,
                    capture=True
                )
                if success:
                    # Check if renderer is set to vulkan
                    vulkan_set = False
                    try:
                        renderer_success, renderer_stdout, _ = self.run_command(
                            [str(wine), "reg", "query", "HKEY_CURRENT_USER\\Software\\Wine\\Direct3D", "/v", "renderer"],
                            check=False,
                            env=env,
                            capture=True
                        )
                        if renderer_success and "vulkan" in renderer_stdout.lower():
                            vulkan_set = True
                    except Exception:
                        pass
                    
                    if vulkan_set:
                        self.log(f"  Vulkan Renderer: ✓ Configured", "success")
                    else:
                        self.log(f"  Vulkan Renderer: ⚠ Not configured", "warning")
                else:
                    self.log(f"  Vulkan Renderer: ✗ Not configured", "error")
            except Exception:
                self.log(f"  Vulkan Renderer: ✗ Not configured", "error")
            
            # Check WebView2 Runtime
            self.log("WebView2 Runtime:", "info")
            if self.check_webview2_installed():
                self.log(f"  Microsoft Edge WebView2 Runtime: ✓ Installed", "success")
            else:
                self.log(f"  Microsoft Edge WebView2 Runtime: ✗ Not installed", "error")
        
        self.log("", "info")  # Empty line for spacing
        
        # Update button states
        for app_name, button in self.update_buttons.items():
            if button is None:
                continue
            
            # Button should be enabled only if Wine is set up AND the app is installed
            is_installed = app_status.get(app_name, False)
            enabled = wine_exists and is_installed
            
            button.setEnabled(enabled)
            if enabled:
                # Reset to default style
                button.setStyleSheet("")
    
    def center_window(self):
        """Center window on screen"""
        frame = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
    
    def setup_zoom(self):
        """Setup zoom in/out functionality for log area"""
        # Zoom in: Ctrl+Plus or Ctrl+=
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+Plus"), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)
        zoom_in_shortcut_alt = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut_alt.activated.connect(self.zoom_in)
        
        # Zoom out: Ctrl+Minus or Ctrl+-
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+Minus"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)
        zoom_out_shortcut_alt = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut_alt.activated.connect(self.zoom_out)
        
        # Reset zoom: Ctrl+0
        zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset_shortcut.activated.connect(self.zoom_reset)
    
    def zoom_in(self):
        """Zoom in (increase font size)"""
        if not hasattr(self, 'log_text') or not self.log_text:
            return
        
        new_size = min(self.log_font_size + 1, 48)
        if new_size != self.log_font_size:
            self.log_font_size = new_size
            font = QFont("Consolas", self.log_font_size)
            self.log_text.setFont(font)
            # Also set document default font to affect HTML content
            self.log_text.document().setDefaultFont(font)
            self.update_zoom_buttons()
    
    def zoom_out(self):
        """Zoom out (decrease font size)"""
        if not hasattr(self, 'log_text') or not self.log_text:
            return
        
        new_size = max(self.log_font_size - 1, 6)
        if new_size != self.log_font_size:
            self.log_font_size = new_size
            font = QFont("Consolas", self.log_font_size)
            self.log_text.setFont(font)
            # Also set document default font to affect HTML content
            self.log_text.document().setDefaultFont(font)
            self.update_zoom_buttons()
    
    def zoom_reset(self):
        """Reset zoom to default size"""
        if not hasattr(self, 'log_text') or not self.log_text:
            return
        
        self.log_font_size = 11
        font = QFont("Consolas", 11)
        self.log_text.setFont(font)
        # Also set document default font to affect HTML content
        self.log_text.document().setDefaultFont(font)
        self.update_zoom_buttons()
    
    def update_zoom_buttons(self):
        """Update zoom button states"""
        try:
            if hasattr(self, 'log_text') and self.log_text:
                current_font = self.log_text.currentFont()
                current_size = current_font.pointSize() if current_font else self.log_font_size
                
                if hasattr(self, 'zoom_in_btn'):
                    self.zoom_in_btn.setEnabled(current_size < 48)
                if hasattr(self, 'zoom_out_btn'):
                    self.zoom_out_btn.setEnabled(current_size > 6)
        except Exception:
            pass
    
    def get_icon_path(self, icon_name):
        """Get the path to a light or dark icon based on theme"""
        if not icon_name:
            return None
        
        icons_dir = Path(__file__).parent / "icons"
        theme_suffix = "light" if self.dark_mode else "dark"
        
        # Check for theme-specific icon first
        themed_icon_path = icons_dir / f"{icon_name}-{theme_suffix}.svg"
        if themed_icon_path.exists():
            return themed_icon_path
        
        # Fallback to base icon name if theme-specific one doesn't exist
        base_icon_path = icons_dir / f"{icon_name}.svg"
        if base_icon_path.exists():
            return base_icon_path
        
        return None

    def _update_button_icons(self):
        """Update all button icons to match the current theme"""
        for btn, icon_name in self.icon_buttons:
            icon_path = self.get_icon_path(icon_name)
            if icon_path:
                icon = QIcon(str(icon_path))
                btn.setIcon(icon)

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
        # Update theme button
        if self.dark_mode:
            self.theme_toggle_btn.setText("☀")
            self.theme_toggle_btn.setToolTip("Switch to Light Mode")
        else:
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("Switch to Dark Mode")
        
        # Update button icons
        self._update_button_icons()
        
        # Update top bar
        self._update_top_bar_style()
        
        # Update theme button style
        self._update_theme_button_style()
        
        # Update scroll area
        self._update_right_scroll_style()
        
        # Update progress label
        self._update_progress_label_style()
    
    def apply_theme(self):
        """Apply current theme (dark or light)"""
        if self.dark_mode:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1c1c1c;
            }
            QWidget {
                background-color: #1c1c1c;
                color: #dcdcdc;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #2d2d2d;
                background-color: #252526;
                margin-top: 8px;
                padding-top: 12px;
                border-radius: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                background-color: #3c3c3c;
                color: #dcdcdc;
                font-weight: bold;
                font-size: 10px;
                border-radius: 4px;
                margin-left: 10px;
            }
            QFrame {
                background-color: #252526;
                border: none;
                border-radius: 0px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555555;
                padding: 8px 12px;
                min-height: 28px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #6a6a6a;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #555555;
                border-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
                border-color: #4a4a4a;
            }
            QPushButton[class="primary"] {
                background-color: #6b8e6b;
                color: #000000;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #5a7a5a;
            }
            QPushButton[class="primary"]:hover {
                background-color: #7a9e7a;
                border-color: #6b8e6b;
                color: #000000;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #d4d4d4;
                border: 1px solid #333333;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border-radius: 8px;
                selection-background-color: #007acc;
                padding: 8px;
            }
            QProgressBar {
                border: none;
                background-color: #2d2d30;
                height: 10px;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8ff361, stop:1 #9af471);
                border-radius: 5px;
            }
            QLabel {
                color: #dcdcdc;
            }
            QToolTip {
                background-color: #2d2d30;
                color: #dcdcdc;
                border: 1px solid #4a4a4a;
                padding: 6px;
                border-radius: 4px;
                font-size: 10px;
            }
            QDialog {
                background-color: #252526;
                border-radius: 12px;
            }
            QMessageBox {
                background-color: #252526;
                border-radius: 12px;
            }
            QRadioButton {
                color: #dcdcdc;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #555555;
                background-color: #3c3c3c;
            }
            QRadioButton::indicator:hover {
                border-color: #6a6a6a;
            }
            QRadioButton::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            QDialogButtonBox QPushButton {
                border-radius: 8px;
                min-width: 80px;
                padding: 8px 16px;
            }
            QPushButton[zoomButton="true"] {
                background-color: #2d2d2d;
                color: #dcdcdc;
                border: 1px solid #4a4a4a;
                padding: 4px 8px;
                min-height: 24px;
                max-width: 35px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton[zoomButton="true"]:hover {
                background-color: #3c3c3c;
                border-color: #5a5a5a;
            }
            QPushButton[zoomButton="true"]:disabled {
                background-color: #252526;
                color: #555555;
                border-color: #2d2d2d;
            }
            QPushButton[cancelButton="true"] {
                background-color: #c74e4e;
                color: #ffffff;
                border: 1px solid #a33a3a;
                padding: 4px 8px;
                min-height: 24px;
                max-width: 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton[cancelButton="true"]:hover {
                background-color: #d95f5f;
                border-color: #b74a4a;
            }
            QPushButton[cancelButton="true"]:pressed {
                background-color: #a33a3a;
            }
        """)
    
    def _apply_light_theme(self):
        """Apply modern light theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #2d2d2d;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
                margin-top: 8px;
                padding-top: 12px;
                border-radius: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px;
                background-color: #e0e0e0;
                color: #2d2d2d;
                font-weight: bold;
                font-size: 10px;
                border-radius: 4px;
                margin-left: 10px;
            }
            QFrame {
                background-color: #ffffff;
                border: none;
                border-radius: 0px;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: #2d2d2d;
                border: 1px solid #c0c0c0;
                padding: 8px 12px;
                min-height: 28px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #a0a0a0;
                color: #1a1a1a;
            }
            QPushButton:disabled, QPushButton[class="primary"]:disabled {
                background-color: #e0e0e0;
                color: #a0a0a0;
                border: 1px solid #c5c5c5;
            }
            QPushButton[class="primary"] {
                background-color: #9bc49b;
                color: #1c1c1c;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #8ab48a;
            }
            QPushButton[class="primary"]:hover {
                background-color: #a8d0a8;
                border-color: #9bc49b;
            }
            QTextEdit {
                background-color: #fafafa;
                color: #1a1a1a;
                border: 1px solid #d0d0d0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border-radius: 8px;
                selection-background-color: #b3d9ff;
                padding: 8px;
            }
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                height: 10px;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #66bb6a);
                border-radius: 5px;
            }
            QLabel {
                color: #2d2d2d;
            }
            QToolTip {
                background-color: #ffffff;
                color: #2d2d2d;
                border: 1px solid #c0c0c0;
                padding: 6px;
                border-radius: 4px;
                font-size: 10px;
            }
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QMessageBox {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QRadioButton {
                color: #2d2d2d;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #c0c0c0;
                background-color: #f5f5f5;
            }
            QRadioButton::indicator:hover {
                border-color: #a0a0a0;
            }
            QRadioButton::indicator:checked {
                background-color: #4caf50;
                border-color: #4caf50;
            }
            QDialogButtonBox QPushButton {
                border-radius: 8px;
                min-width: 80px;
                padding: 8px 16px;
            }
            QPushButton[zoomButton="true"] {
                background-color: #e0e0e0;
                color: #2d2d2d;
                border: 1px solid #c0c0c0;
                padding: 4px 8px;
                min-height: 24px;
                max-width: 35px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton[zoomButton="true"]:hover {
                background-color: #d0d0d0;
                border-color: #a0a0a0;
            }
            QPushButton[zoomButton="true"]:disabled {
                background-color: #e0e0e0;
                color: #a0a0a0;
                border-color: #c5c5c5;
            }
            QPushButton[cancelButton="true"] {
                background-color: #f44336;
                color: #ffffff;
                border: 1px solid #d32f2f;
                padding: 4px 8px;
                min-height: 24px;
                max-width: 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton[cancelButton="true"]:hover {
                background-color: #e57373;
                border-color: #ef5350;
            }
            QPushButton[cancelButton="true"]:pressed {
                background-color: #d32f2f;
            }
        """)
    
    def _update_theme_button_style(self):
        """Update theme toggle button styling based on current theme"""
        if hasattr(self, 'theme_toggle_btn'):
            if self.dark_mode:
                self.theme_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: #f0f0f0;
                        border: 1px solid #555555;
                        padding: 0px;
                        min-height: 32px;
                        max-height: 32px;
                        min-width: 40px;
                        max-width: 40px;
                        font-size: 18px;
                        border-radius: 6px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #4a4a4a;
                        border-color: #6a6a6a;
                    }
                """)
            else:
                self.theme_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        color: #2d2d2d;
                        border: 1px solid #c0c0c0;
                        padding: 0px;
                        min-height: 32px;
                        max-height: 32px;
                        min-width: 40px;
                        max-width: 40px;
                        font-size: 18px;
                        border-radius: 6px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                        border-color: #a0a0a0;
                    }
                """)
    
    def _update_top_bar_style(self):
        """Update top bar styling based on current theme"""
        if hasattr(self, 'top_bar'):
            if self.dark_mode:
                self.top_bar.setStyleSheet(
                    "background-color: #2d2d2d; padding: 10px 15px; "
                    "border-top-left-radius: 8px; border-top-right-radius: 8px;"
                )
            else:
                self.top_bar.setStyleSheet(
                    "background-color: #e8e8e8; padding: 10px 15px; "
                    "border-top-left-radius: 8px; border-top-right-radius: 8px;"
                )
        
        if hasattr(self, 'title_label'):
            if self.dark_mode:
                self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
            else:
                self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a;")
    
    def _update_right_scroll_style(self):
        """Update right scroll area styling based on current theme"""
        if hasattr(self, 'right_scroll'):
            if self.dark_mode:
                self.right_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #1c1c1c;
                        border: none;
                    }
                    QScrollBar:vertical {
                        background-color: #1c1c1c;
                        width: 12px;
                        border-radius: 6px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: #3c3c3c;
                        border-radius: 6px;
                        min-height: 30px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background-color: #4a4a4a;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                    }
                """)
            else:
                self.right_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #f5f5f5;
                        border: none;
                    }
                    QScrollBar:vertical {
                        background-color: #f5f5f5;
                        width: 12px;
                        border-radius: 6px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: #c0c0c0;
                        border-radius: 6px;
                        min-height: 30px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background-color: #a0a0a0;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                    }
                """)
    
    def _update_progress_label_style(self):
        """Update progress label styling based on current theme"""
        if hasattr(self, 'progress_label'):
            if self.dark_mode:
                self.progress_label.setStyleSheet(
                    "font-size: 11px; font-weight: 500; color: #dcdcdc; "
                    "padding: 5px 10px; background-color: #2d2d2d; border-radius: 4px;"
                )
            else:
                self.progress_label.setStyleSheet(
                    "font-size: 11px; font-weight: 500; color: #2d2d2d; "
                    "padding: 5px 10px; background-color: #e0e0e0; border-radius: 4px;"
                )
    
    def create_ui(self):
        """Create the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(1, 1, 1, 1)
        
        # Top bar
        self.top_bar = QFrame()
        self.top_bar.setStyleSheet("background-color: #2d2d2d; padding: 10px 15px; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(15, 10, 15, 10)
        
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
                    svg_widget.setFixedSize(32, 32)
                    svg_widget.setStyleSheet("background: transparent;")
                    top_bar_layout.addWidget(svg_widget)
                    top_bar_layout.addSpacing(5)
                except Exception:
                    # Fallback to QIcon if QSvgWidget fails
                    icon = QIcon(self.affinity_icon_path)
                    self.setWindowIcon(icon)
                    
                    icon_label = QLabel()
                    pixmap = icon.pixmap(32, 32)
                    if not pixmap.isNull():
                        icon_label.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        icon_label.setFixedSize(32, 32)
                        top_bar_layout.addWidget(icon_label)
                        top_bar_layout.addSpacing(5)
            except Exception as e:
                pass  # If icon loading fails, continue without icon
        
        self.title_label = QLabel("Affinity on Linux Installer")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()
        
        # Add system status indicator in top bar
        self.system_status_label = QLabel("●")
        self.system_status_label.setStyleSheet(
            "font-size: 14px; color: #666666; padding: 0 5px;"
        )
        self.system_status_label.setToolTip("System Status: Initializing...")
        top_bar_layout.addWidget(self.system_status_label)
        top_bar_layout.addSpacing(12)
        
        # Add theme toggle button
        self.theme_toggle_btn = QPushButton("☀")
        self.theme_toggle_btn.setToolTip("Switch to Light Mode")
        self.theme_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555555;
                padding: 0px;
                min-height: 32px;
                max-height: 32px;
                min-width: 40px;
                max-width: 40px;
                font-size: 18px;
                border-radius: 6px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #6a6a6a;
            }
        """)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        top_bar_layout.addWidget(self.theme_toggle_btn)
        
        main_layout.addWidget(self.top_bar)
        
        # Content area with scroll support
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Status/Log
        left_panel = self.create_status_section()
        content_layout.addWidget(left_panel, stretch=3)
        
        # Right panel - Buttons (wrapped in scroll area for small screens)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.right_scroll = right_scroll  # Store reference for theme updates
        self._update_right_scroll_style()
        
        right_panel = self.create_button_sections()
        right_scroll.setWidget(right_panel)
        right_scroll.setMinimumWidth(320)
        right_scroll.setMaximumWidth(400)
        
        content_layout.addWidget(right_scroll, stretch=1)
        
        main_layout.addWidget(content_widget, stretch=1)
    
    def create_status_section(self):
        """Create the status/log output section"""
        group = QGroupBox("Status & Log Output")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        group_layout.setContentsMargins(12, 22, 12, 12)
        
        # Progress status label (above progress bar)
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet(
            "font-size: 11px; font-weight: 500; color: #dcdcdc; "
            "padding: 5px 10px; background-color: #2d2d2d; border-radius: 4px;"
        )
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(self.progress_label)
        
        # Progress bar and cancel button container
        progress_container = QWidget()
        progress_container_layout = QHBoxLayout(progress_container)
        progress_container_layout.setContentsMargins(0, 0, 0, 0)
        progress_container_layout.setSpacing(8)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        progress_container_layout.addWidget(self.progress, stretch=1)
        
        # Cancel button (hidden by default)
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setToolTip("Cancel current operation")
        self.cancel_btn.setProperty("cancelButton", True)
        self.cancel_btn.setMaximumWidth(30)
        self.cancel_btn.setMinimumWidth(30)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        progress_container_layout.addWidget(self.cancel_btn)
        
        group_layout.addWidget(progress_container)
        
        # Log and zoom controls container
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 5, 0, 0)
        log_layout.setSpacing(5)

        # Zoom controls
        zoom_container = QWidget()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(5)
        zoom_layout.addStretch()
        
        # Get icon path
        icons_dir = Path(__file__).parent / "icons"
        
        # Zoom out button
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setProperty("zoomButton", True)
        self.zoom_out_btn.setMaximumWidth(35)
        self.zoom_out_btn.setMinimumWidth(35)
        icon_name_zoom_out = "zoom-out"
        icon_path_zoom_out = self.get_icon_path(icon_name_zoom_out)
        if icon_path_zoom_out:
            self.zoom_out_btn.setIcon(QIcon(str(icon_path_zoom_out)))
        self.zoom_out_btn.setIconSize(QSize(16, 16))
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        self.icon_buttons.append((self.zoom_out_btn, icon_name_zoom_out))

        # Zoom reset button
        self.zoom_reset_btn = QPushButton()
        self.zoom_reset_btn.setToolTip("Reset Zoom (Ctrl+0)")
        self.zoom_reset_btn.setProperty("zoomButton", True)
        self.zoom_reset_btn.setMaximumWidth(35)
        self.zoom_reset_btn.setMinimumWidth(35)
        icon_name_zoom_reset = "zoom-original"
        icon_path_zoom_reset = self.get_icon_path(icon_name_zoom_reset)
        if icon_path_zoom_reset:
            self.zoom_reset_btn.setIcon(QIcon(str(icon_path_zoom_reset)))
        self.zoom_reset_btn.setIconSize(QSize(16, 16))
        self.zoom_reset_btn.clicked.connect(self.zoom_reset)
        zoom_layout.addWidget(self.zoom_reset_btn)
        self.icon_buttons.append((self.zoom_reset_btn, icon_name_zoom_reset))

        # Zoom in button
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.setProperty("zoomButton", True)
        self.zoom_in_btn.setMaximumWidth(35)
        self.zoom_in_btn.setMinimumWidth(35)
        icon_name_zoom_in = "zoom-in"
        icon_path_zoom_in = self.get_icon_path(icon_name_zoom_in)
        if icon_path_zoom_in:
            self.zoom_in_btn.setIcon(QIcon(str(icon_path_zoom_in)))
        self.zoom_in_btn.setIconSize(QSize(16, 16))
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        self.icon_buttons.append((self.zoom_in_btn, icon_name_zoom_in))
        
        log_layout.addWidget(zoom_container)
        
        # Log output with zoom support
        self.log_text = ZoomableTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", self.log_font_size))
        self.log_text.set_zoom_callbacks(self.zoom_in, self.zoom_out)
        log_layout.addWidget(self.log_text)
        
        group_layout.addWidget(log_container)
        
        # Initialize zoom button states
        self.update_zoom_buttons()
        
        return group
    
    def create_button_sections(self):
        """Create organized button sections"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(8)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Get icon path helper
        icons_dir = Path(__file__).parent / "icons"
        
        # Quick Start section - One-click install
        quick_group = self.create_button_group(
            "Quick Start",
            [
                ("One-Click Full Setup", self.one_click_setup, "Setup Wine, dependencies, and prepare for Affinity installation", "rocket"),
                ("Setup Wine Environment", self.setup_wine_environment, "Download and configure Wine environment only", "wine"),
                ("Install System Dependencies", self.install_system_dependencies, "Install required Linux packages", "dependencies"),
                ("Install Winetricks Dependencies", self.install_winetricks_deps, "Install Windows components (.NET, fonts, etc.)", "wand"),
            ]
        )
        container_layout.addWidget(quick_group)
        
        # System Setup section
        sys_group = self.create_button_group(
            "System Setup",
            [
                ("Download Affinity Installer", self.download_affinity_installer, "Download the latest Affinity installer from official source", "download"),
                ("Install from File Manager", self.install_from_file, "Install Affinity or any Windows app from a local .exe file", "folderopen"),
            ]
        )
        container_layout.addWidget(sys_group)
        
        # Update Affinity Applications section
        app_buttons = [
            ("Affinity (Unified)", "Add", "Update or install Affinity V3 unified application", "affinity-unified"),
            ("Affinity Photo", "Photo", "Update or install Affinity Photo for image editing", "camera"),
            ("Affinity Designer", "Designer", "Update or install Affinity Designer for vector graphics", "pen"),
            ("Affinity Publisher", "Publisher", "Update or install Affinity Publisher for page layout", "book"),
        ]
        app_group = self.create_button_group(
            "Update Affinity Applications",
            [(text, lambda name=app_name: self.update_application(name), tooltip, icon) for text, app_name, tooltip, icon in app_buttons],
            button_refs=self.update_buttons,
            button_keys=[app_name for _, app_name, _, _ in app_buttons]
        )
        container_layout.addWidget(app_group)
        
        # Troubleshooting section
        troubleshoot_group = self.create_button_group(
            "Troubleshooting",
            [
                ("Wine Configuration", self.open_winecfg, "Open Wine settings to configure Windows version and libraries", "wine"),
                ("Winetricks", self.open_winetricks, "Install additional Windows components and dependencies", "wand"),
                ("Set Windows 11 + Renderer", self.set_windows11_renderer, "Configure Windows version and graphics renderer (Vulkan/OpenGL)", "windows"),
                ("Reinstall WinMetadata", self.reinstall_winmetadata, "Fix corrupted Windows metadata files", "loop"),
                ("WebView2 Runtime (v3)", self.install_webview2_runtime, "Install WebView2 for Affinity V3 Help system", "chrome"),
                ("Fix Settings (v3)", self.fix_affinity_settings, "Patch Affinity v3 DLL to enable settings saving", "cog"),
                ("Set DPI Scaling", self.set_dpi_scaling, "Adjust interface size for better readability", "scale"),
                ("Uninstall", self.uninstall_affinity_linux, "Completely remove Affinity Linux installation", "trash"),
            ]
        )
        container_layout.addWidget(troubleshoot_group)
        
        # Launch section
        launch_group = self.create_button_group(
            "Launch",
            [
                ("Launch Affinity v3", self.launch_affinity_v3, "Start Affinity V3 unified application", "play"),
            ]
        )
        container_layout.addWidget(launch_group)
        
        # Other section
        other_group = self.create_button_group(
            "Other",
            [
                ("Exit", self.close, "Close the installer", "exit"),
            ]
        )
        container_layout.addWidget(other_group)
        
        container_layout.addStretch()
        
        return container
    
    def create_button_group(self, title, buttons, button_refs=None, button_keys=None):
        """Create a grouped button section"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(4)
        group_layout.setContentsMargins(10, 20, 10, 10)
        
        for idx, button_data in enumerate(buttons):
            # Handle (text, command), (text, command, tooltip), (text, command, tooltip, icon) formats
            tooltip = None
            icon_name = None
            if len(button_data) == 2:
                text, command = button_data
            elif len(button_data) == 3:
                text, command, tooltip = button_data
            elif len(button_data) == 4:
                text, command, tooltip, icon_name = button_data
            else:
                text, command = button_data[0], button_data[1]
            
            btn = QPushButton(text)
            # Wrap click to track the button and delegate to original command
            btn.clicked.connect(lambda checked=False, b=btn, cmd=command: self._handle_button_click(b, cmd))
            
            # Add icon if provided
            if icon_name:
                icon_path = self.get_icon_path(icon_name)
                if icon_path:
                    icon = QIcon(str(icon_path))
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(16, 16))
                    self.icon_buttons.append((btn, icon_name))  # Store button and icon name
            
            # Add tooltip if provided
            if tooltip:
                btn.setToolTip(tooltip)
            
            # Set primary class for the main call-to-action button
            if text == "One-Click Full Setup":
                btn.setProperty("class", "primary")
            
            group_layout.addWidget(btn)
            
            # Store button reference if requested
            if button_refs is not None and button_keys is not None and idx < len(button_keys):
                button_refs[button_keys[idx]] = btn
        
        return group
    
    def _handle_button_click(self, button, command):
        """Record last clicked button and invoke the original command."""
        try:
            self._last_clicked_button = button
            command()
        except Exception as e:
            # If command failed immediately, do not leave spinner state queued
            self._last_clicked_button = None
            self.log(f"Error executing command: {e}", "error")
    
    def _show_spinner_safe(self, button):
        """Replace the given button's icon with a rotating spinner (UI thread)."""
        try:
            if button is None or not isinstance(button, QPushButton):
                return
            # If already spinning, do nothing
            if button in self._button_spinner_map:
                return
            # Determine size from existing icon size or button height
            current_size = button.iconSize()
            size = max(16, max(current_size.width(), current_size.height())) if current_size.isValid() else max(20, button.sizeHint().height() - 6)
            color = QColor('#8ff361') if self.dark_mode else QColor('#4caf50')
            # Prepare state
            state = {
                'angle': 0,
                'timer': QTimer(self),
                'orig_icon': button.icon(),
                'orig_size': current_size if current_size.isValid() else QSize(size, size),
                'size': size,
                'color': color,
            }
            def tick():
                state['angle'] = (state['angle'] - 30) % 360
                # Draw spinner pixmap
                pm = QPixmap(state['size'], state['size'])
                pm.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pm)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                lw = max(2, int(state['size'] * 0.12))
                rect = pm.rect().adjusted(lw, lw, -lw, -lw)
                pen = QPen(state['color'])
                pen.setWidth(lw)
                painter.setPen(pen)
                start_angle = int(state['angle'] * 16)
                span_angle = int(270 * 16)
                painter.drawArc(rect, start_angle, span_angle)
                painter.end()
                button.setIcon(QIcon(pm))
                button.setIconSize(QSize(state['size'], state['size']))
            t = state['timer']
            t.setInterval(50)
            t.timeout.connect(tick)
            t.start()
            # Draw initial frame immediately
            tick()
            self._button_spinner_map[button] = state
        except Exception:
            pass
    
    def _hide_spinner_safe(self, button):
        """Restore the button's original icon (UI thread)."""
        try:
            state = self._button_spinner_map.pop(button, None)
            if state is None:
                return
            timer = state.get('timer')
            if timer:
                try:
                    timer.stop()
                except Exception:
                    pass
            orig_icon = state.get('orig_icon')
            orig_size = state.get('orig_size')
            if isinstance(button, QPushButton):
                if orig_icon is not None:
                    button.setIcon(orig_icon)
                if orig_size is not None and orig_size.isValid():
                    button.setIconSize(orig_size)
        except Exception:
            pass
    
    def load_affinity_icon(self):
        """Download and load Affinity V3 icon"""
        try:
            icon_dir = Path.home() / ".local" / "share" / "icons"
            icon_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icon_dir / "Affinity.svg"
            
            # Check if file exists and is valid SVG
            needs_download = True
            if icon_path.exists():
                try:
                    # Check if file is valid SVG (not HTML)
                    with open(icon_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        # Valid SVG should start with <?xml or <svg, not <!DOCTYPE or <html
                        if first_line.startswith('<?xml') or first_line.startswith('<svg'):
                            needs_download = False
                        else:
                            # File is corrupted (likely HTML), delete it
                            icon_path.unlink()
                except Exception:
                    # If we can't read it, delete and re-download
                    try:
                        icon_path.unlink()
                    except Exception:
                        pass
            
            # Download if needed
            if needs_download:
                icon_url = "https://raw.githubusercontent.com/seapear/AffinityOnLinux/main/Assets/Icons/Affinity-Canva.svg"
                try:
                    urllib.request.urlretrieve(icon_url, str(icon_path))
                    self.affinity_icon_path = str(icon_path)
                except Exception as e:
                    self.affinity_icon_path = None
            else:
                self.affinity_icon_path = str(icon_path)
        except Exception as e:
            self.affinity_icon_path = None
    
    def closeEvent(self, event):
        """Handle window close event - close log file"""
        if self.log_file:
            try:
                log_footer = f"{'='*80}\n"
                log_footer += f"Session Ended: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                log_footer += f"{'='*80}\n\n"
                self.log_file.write(log_footer)
                self.log_file.close()
            except Exception:
                pass
        event.accept()
    
    def sanitize_filename(self, filename):
        """Sanitize filename by replacing spaces and other problematic characters"""
        # Replace spaces with dashes
        sanitized = filename.replace(" ", "-")
        # Remove other potentially problematic characters
        sanitized = sanitized.replace("(", "-").replace(")", "-")
        sanitized = sanitized.replace("[", "-").replace("]", "-")
        # Keep only one consecutive dash
        while "--" in sanitized:
            sanitized = sanitized.replace("--", "-")
        return sanitized
    
    def log(self, message, level="info"):
        """Add message to log (thread-safe via signal)"""
        self.log_signal.emit(message, level)
    
    def _init_log_file(self):
        """Initialize log file"""
        try:
            # Open log file in append mode
            self.log_file = open(self.log_file_path, 'a', encoding='utf-8')
            # Write header
            log_header = f"\n{'='*80}\n"
            log_header += f"Affinity Linux Installer - Session Started\n"
            log_header += f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            log_header += f"{'='*80}\n"
            self.log_file.write(log_header)
            self.log_file.flush()
        except Exception as e:
            # If we can't open the log file, continue without file logging
            self.log_file = None
    
    def _log_safe(self, message, level="info"):
        """Thread-safe log handler (called from main thread)"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Determine icon, color, and styling based on level
        if level == "error":
            icon = "❌"
            color = "#ff7b72"
            bg_color = "rgba(255, 123, 114, 0.1)"
            icon_color = "#ff7b72"
        elif level == "success":
            icon = "✔"
            color = "#6a9955"
            bg_color = "rgba(106, 153, 85, 0.1)"
            icon_color = "#6a9955"
        elif level == "warning":
            icon = "⚠️"
            color = "#cd9731"
            bg_color = "rgba(205, 151, 49, 0.1)"
            icon_color = "#cd9731"
        else:
            icon = "•"
            color = "#9cdcfe"
            bg_color = "transparent"
            icon_color = "#569cd6"

        # Sanitize message to prevent HTML injection issues
        message = message.replace("<", "&lt;").replace(">", "&gt;")

        # Format message with better styling
        timestamp_html = f'<span style="color: #6c7886; font-weight: 500;">[{timestamp}]</span>'
        icon_html = f'<span style="color: {icon_color}; font-weight: bold; font-size: 12px;">{icon}</span>'
        
        # Add subtle background for important messages
        if level in ["error", "success", "warning"]:
            full_message = f'<div style="background-color: {bg_color}; padding: 4px 8px; margin: 2px 0; border-radius: 4px; border-left: 3px solid {icon_color};">{timestamp_html} {icon_html} <span style="color: {color};">{message}</span></div>'
        else:
            full_message = f'<div style="padding: 2px 4px; margin: 1px 0;">{timestamp_html} {icon_html} <span style="color: {color};">{message}</span></div>'
        
        self.log_text.append(full_message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Write to log file (plain text, no HTML)
        if self.log_file:
            try:
                # Create a plain text version for the log file
                plain_message = f"[{timestamp}] [{level.upper()}] {message}"
                self.log_file.write(plain_message + "\n")
                self.log_file.flush()  # Ensure it's written immediately
            except Exception:
                # If file write fails, continue without file logging
                pass
    
    def update_progress(self, value):
        """Update progress bar (thread-safe via signal)"""
        self.progress_signal.emit(value)
    
    def _update_progress_safe(self, value):
        """Thread-safe progress update handler (called from main thread)"""
        self.progress.setValue(int(value * 100))
    
    def _update_progress_text_safe(self, text):
        """Thread-safe progress text update handler (called from main thread)"""
        self.progress_label.setText(text)
    
    def update_progress_text(self, text):
        """Update progress label text (thread-safe via signal)"""
        self.progress_text_signal.emit(text)
    
    def cancel_operation(self):
        """Cancel the current operation with confirmation"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Cancel Operation",
            f"Are you sure you want to cancel the current operation?\n\n"
            f"Operation: {self.current_operation or 'Unknown'}\n\n"
            f"Note: This may leave the installation in an incomplete state.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.operation_cancelled = True
            # Signal cancellation early so running commands can stop
            self.cancel_event.set()
            self.update_progress_text("Cancelling...")
            # Terminate any active subprocesses
            try:
                self.terminate_active_processes()
            except Exception:
                pass
            self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "warning")
            self.log("⚠ Operation cancelled by user", "warning")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", "warning")
            self.update_progress_text("Operation cancelled")
            self.update_progress(0.0)  # Reset progress bar
            self.cancel_btn.setVisible(False)
            self.operation_in_progress = False
            # Ensure spinner is restored on cancel
            try:
                if self._operation_button is not None:
                    self.hide_spinner_signal.emit(self._operation_button)
            except Exception:
                pass
    
    def start_operation(self, operation_name):
        """Mark the start of an operation and show cancel button"""
        self.operation_cancelled = False
        self.cancel_event.clear()
        self.current_operation = operation_name
        self.operation_in_progress = True
        # Replace last clicked button with spinner (on UI thread)
        if self._last_clicked_button is not None:
            self._operation_button = self._last_clicked_button
            self.show_spinner_signal.emit(self._operation_button)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(True)
    
    def end_operation(self):
        """Mark the end of an operation: restore UI, reset progress, toggle cancel."""
        self.operation_in_progress = False
        self.current_operation = None
        # Toggle cancel button off
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setVisible(False)
        # Restore button icon (stop spinner)
        if self._operation_button is not None:
            self.hide_spinner_signal.emit(self._operation_button)
            self._operation_button = None
            self._last_clicked_button = None
        # Always restore progress bar/text to idle state
        self.update_progress(0.0)
        self.update_progress_text("Ready")
    
    def check_cancelled(self):
        """Check if operation was cancelled"""
        if self.operation_cancelled:
            self.end_operation()
            return True
        return False
    
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
    
    def _request_sudo_password_safe(self):
        """Request sudo password from user (called from main thread)"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Administrator Authentication Required")
        dialog.setMinimumWidth(400)
        dialog.setModal(True)  # Ensure dialog is modal
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)  # Keep on top
        
        layout = QVBoxLayout(dialog)
        
        # Add explanation label
        label = QLabel(
            "This operation requires administrator privileges.\n\n"
            "Please enter your password to continue:"
        )
        layout.addWidget(label)
        
        # Add password input
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Enter your password")
        layout.addWidget(password_input)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Allow Enter key to submit
        password_input.returnPressed.connect(dialog.accept)
        
        # Ensure dialog is visible and raised
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        
        # Focus the password input
        password_input.setFocus()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.sudo_password = password_input.text()
        else:
            self.sudo_password = None
    
    def get_sudo_password(self):
        """Get sudo password from user (thread-safe)"""
        # If we already have a validated password, return it
        if self.sudo_password_validated and self.sudo_password:
            return self.sudo_password
        
        # Request password from main thread
        self.sudo_password = None
        self.sudo_password_dialog_signal.emit()
        
        # Wait for password to be entered (with timeout)
        max_wait = 300  # 30 seconds timeout
        waited = 0
        while self.sudo_password is None and waited < max_wait:
            time.sleep(0.1)
            waited += 1
        
        return self.sudo_password
    
    def validate_sudo_password(self, password):
        """Validate sudo password by running a test command"""
        try:
            # Set up environment for sudo
            env = os.environ.copy()
            # Unset SUDO_ASKPASS to force sudo to read password from stdin via -S flag
            # This prevents errors when askpass programs (like ksshaskpass) don't exist
            env.pop('SUDO_ASKPASS', None)
            
            # Test the password with a harmless sudo command
            process = subprocess.Popen(
                ["sudo", "-S", "true"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Send password and wait for completion with timeout
            try:
                stdout, stderr = process.communicate(input=f"{password}\n", timeout=15)
            except subprocess.TimeoutExpired:
                # Timeout occurred, terminate the process and all its children
                try:
                    # Try to kill the process group first
                    if process.pid:
                        try:
                            pgid = os.getpgid(process.pid)
                            os.killpg(pgid, signal.SIGTERM)
                            time.sleep(0.5)
                            # Force kill if still running
                            if process.poll() is None:
                                os.killpg(pgid, signal.SIGKILL)
                        except (ProcessLookupError, OSError, AttributeError):
                            # Process group doesn't exist or process already terminated
                            process.kill()
                except Exception:
                    # Fallback to simple kill
                    try:
                        process.kill()
                    except Exception:
                        pass
                try:
                    process.communicate()
                except Exception:
                    pass
                self.log("Password validation timed out - sudo may be waiting for input", "error")
                self.sudo_password_validated = False
                return False
            except Exception as e:
                # Other I/O errors - check if process succeeded anyway
                try:
                    if process.poll() is None:
                        process.wait(timeout=1)
                except Exception:
                    pass
                # If return code is 0, validation succeeded despite the error
                if process.returncode == 0:
                    self.sudo_password_validated = True
                    return True
                self.log(f"Error validating sudo password: {e}", "error")
                self.sudo_password_validated = False
                return False
            
            if process.returncode == 0:
                self.sudo_password_validated = True
                return True
            else:
                # Check stderr for more details
                if stderr:
                    error_msg = stderr.strip()
                    if "incorrect password" in error_msg.lower() or "sorry" in error_msg.lower():
                        self.log("Incorrect password", "error")
                    else:
                        self.log(f"Password validation failed: {error_msg}", "error")
                else:
                    self.log("Password validation failed", "error")
                self.sudo_password_validated = False
                return False
        except Exception as e:
            self.log(f"Error validating sudo password: {e}", "error")
            self.sudo_password_validated = False
            return False
    
    def _request_interactive_response_safe(self, prompt_text, default_response):
        """Request user response to interactive prompt (called from main thread)"""
        # Parse the prompt to determine type
        prompt_lower = prompt_text.lower()
        
        # Detect yes/no questions
        if any(pattern in prompt_lower for pattern in ["(y/n)", "[y/n]", "yes/no", "overwrite?"]):
            # Extract default from prompt
            default_yes = "y" in default_response.lower() if default_response else False
            
            reply = QMessageBox.question(
                self,
                "User Input Required",
                prompt_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.interactive_response = "y\n"
            else:
                self.interactive_response = "n\n"
        else:
            # For other prompts, use input dialog
            response, ok = QInputDialog.getText(
                self,
                "User Input Required",
                prompt_text,
                QLineEdit.EchoMode.Normal,
                default_response or ""
            )
            
            if ok:
                self.interactive_response = response + "\n"
            else:
                self.interactive_response = "\n"  # Empty response (just Enter)
        
        self.waiting_for_response = False
    
    def get_interactive_response(self, prompt_text, default_response=""):
        """Get user response to interactive prompt (thread-safe)"""
        self.interactive_response = None
        self.waiting_for_response = True
        self.interactive_prompt_signal.emit(prompt_text, default_response)
        
        # Wait for response with timeout
        max_wait = 300  # 30 seconds
        waited = 0
        while self.waiting_for_response and waited < max_wait:
            time.sleep(0.1)
            waited += 1
        
        return self.interactive_response or "\n"
    
    def _show_question_dialog_safe(self, title, message, buttons):
        """Show question dialog (called from main thread)"""
        # Convert button list to QMessageBox buttons
        qbuttons = QMessageBox.StandardButton.NoButton
        for btn in buttons:
            if btn == "Yes":
                qbuttons |= QMessageBox.StandardButton.Yes
            elif btn == "No":
                qbuttons |= QMessageBox.StandardButton.No
            elif btn == "Retry":
                qbuttons |= QMessageBox.StandardButton.Retry
            elif btn == "Cancel":
                qbuttons |= QMessageBox.StandardButton.Cancel
        
        reply = QMessageBox.question(self, title, message, qbuttons)
        
        # Store response
        if reply == QMessageBox.StandardButton.Yes:
            self.question_dialog_response = "Yes"
        elif reply == QMessageBox.StandardButton.No:
            self.question_dialog_response = "No"
        elif reply == QMessageBox.StandardButton.Retry:
            self.question_dialog_response = "Retry"
        elif reply == QMessageBox.StandardButton.Cancel:
            self.question_dialog_response = "Cancel"
        else:
            self.question_dialog_response = "Cancel"
        
        self.waiting_for_question_response = False
    
    def show_question_dialog(self, title, message, buttons=["Yes", "No"]):
        """Show question dialog (thread-safe)"""
        self.question_dialog_response = None
        self.waiting_for_question_response = True
        self.question_dialog_signal.emit(title, message, buttons)
        
        # Wait for response with timeout
        max_wait = 300  # 30 seconds
        waited = 0
        while self.waiting_for_question_response and waited < max_wait:
            time.sleep(0.1)
            waited += 1
        
        return self.question_dialog_response or "Cancel"
    
    def _register_process(self, proc):
        """Track a running subprocess for potential cancellation."""
        try:
            with self._process_lock:
                self._active_processes.add(proc)
        except Exception:
            pass
    
    def _unregister_process(self, proc):
        """Stop tracking a subprocess."""
        try:
            with self._process_lock:
                self._active_processes.discard(proc)
        except Exception:
            pass
    
    def _terminate_process(self, proc):
        """Terminate a subprocess and its process group safely."""
        try:
            # Try to terminate the whole process group first
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                proc.terminate()
            # Wait briefly, then force kill if still alive
            try:
                proc.wait(timeout=2)
            except Exception:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        finally:
            self._unregister_process(proc)
    
    def terminate_active_processes(self):
        """Terminate all active subprocesses started by this installer."""
        try:
            with self._process_lock:
                procs = list(self._active_processes)
            for p in procs:
                self._terminate_process(p)
        except Exception:
            pass
    
    def run_command(self, command, check=True, shell=False, capture=True, env=None):
        """Execute shell command with GUI sudo password support and cancellation."""
        try:
            # Convert command to list if it's a string
            if isinstance(command, str) and not shell:
                command = command.split()
            # Ensure command is a list
            if not isinstance(command, list):
                command = list(command)
            
            # Set up environment for non-interactive operation
            if env is None:
                env = os.environ.copy()
            
            # Force non-interactive mode for various tools
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            env['NEEDRESTART_MODE'] = 'a'  # Auto-restart services without asking
            env['DEBIAN_PRIORITY'] = 'critical'
            env['APT_LISTCHANGES_FRONTEND'] = 'none'
            env['LANG'] = 'C'  # Use C locale to avoid encoding issues
            env['LC_ALL'] = 'C'
            
            # Check if this is a sudo command
            is_sudo = isinstance(command, list) and len(command) > 0 and command[0] == "sudo"
            
            # Unset SUDO_ASKPASS to force sudo to read password from stdin via -S flag
            # This prevents errors when askpass programs (like ksshaskpass) don't exist
            if is_sudo:
                env.pop('SUDO_ASKPASS', None)  # Remove SUDO_ASKPASS if it exists
            
            if is_sudo:
                # Get password if needed
                max_attempts = 3
                for attempt in range(max_attempts):
                    if self.cancel_event.is_set():
                        return False, "", "Cancelled"
                    password = self.get_sudo_password()
                    if password is None:
                        self.log("Authentication cancelled by user", "warning")
                        return False, "", "Authentication cancelled"
                    # Validate password first
                    if not self.sudo_password_validated:
                        if self.validate_sudo_password(password):
                            self.log("Authentication successful", "success")
                            break
                        else:
                            self.log("Authentication failed. Please try again.", "error")
                            self.sudo_password = None
                            self.sudo_password_validated = False
                            if attempt == max_attempts - 1:
                                return False, "", "Authentication failed after multiple attempts"
                    else:
                        break
                
                # Run command with password via stdin
                # Add -S flag to read password from stdin if not present
                # Make sure -S is right after "sudo"
                # Create a copy to avoid modifying the original
                command = list(command)
                if len(command) > 1:
                    # Only add -S if it's not already in position 1 (right after sudo)
                    # Don't remove -S that's part of the actual command (like pacman -S)
                    if command[1] != "-S":
                        # Insert -S right after "sudo"
                        command.insert(1, "-S")
                else:
                    # Only "sudo" in command, add -S
                    command.append("-S")
                
                proc = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE if capture else None,
                    stderr=subprocess.PIPE if capture else None,
                    text=True,
                    env=env,  # Use the modified env that has SUDO_ASKPASS removed
                    preexec_fn=os.setsid
                )
                self._register_process(proc)
                try:
                    # Send password to sudo via stdin using communicate() which handles stdin properly
                    password_input = f"{self.sudo_password}\n"
                    
                    if capture:
                        stdout_acc = ""
                        stderr_acc = ""
                        # Read output without timeout for long-running commands like package installation
                        try:
                            # Use communicate with input - this is the safest way
                            out, err = proc.communicate(input=password_input, timeout=None)
                            stdout_acc += out or ""
                            stderr_acc += err or ""
                        except subprocess.TimeoutExpired:
                            # This shouldn't happen with timeout=None, but handle it just in case
                            if self.cancel_event.is_set():
                                self._terminate_process(proc)
                                return False, stdout_acc, "Cancelled"
                            # Force read remaining output
                            try:
                                out, err = proc.communicate()
                                stdout_acc += out or ""
                                stderr_acc += err or ""
                            except Exception:
                                pass
                        except Exception as e:
                            # Catch all exceptions including "I/O operation on closed file"
                            error_msg = str(e)
                            error_type = type(e).__name__
                            
                            # Check if process completed successfully despite the error
                            try:
                                if proc.poll() is None:
                                    # Process still running, wait a bit
                                    proc.wait(timeout=2)
                            except Exception:
                                pass
                            
                            # If return code is 0, the operation succeeded despite the exception
                            if proc.returncode == 0:
                                # Try to read any remaining output
                                try:
                                    if proc.stdout and not proc.stdout.closed:
                                        remaining = proc.stdout.read()
                                        if remaining:
                                            stdout_acc += remaining
                                except Exception:
                                    pass
                                try:
                                    if proc.stderr and not proc.stderr.closed:
                                        remaining = proc.stderr.read()
                                        if remaining:
                                            stderr_acc += remaining
                                except Exception:
                                    pass
                                # Operation succeeded, return success
                                return True, stdout_acc, stderr_acc
                            
                            # Only report error if return code indicates failure
                            if "closed file" in error_msg.lower() or "I/O operation" in error_msg:
                                # This is often a harmless error if the process succeeded
                                if proc.returncode == 0:
                                    return True, stdout_acc, stderr_acc
                                # If it failed, log it
                                self.log(f"Error during command execution ({error_type}): {error_msg}", "error")
                            else:
                                self.log(f"Error during command execution ({error_type}): {error_msg}", "error")
                            
                            self._terminate_process(proc)
                            return False, stdout_acc, stderr_acc or error_msg
                        
                        success = proc.returncode == 0
                        return success, stdout_acc, stderr_acc
                    else:
                        # No capture: send password and wait for completion
                        try:
                            proc.communicate(input=password_input, timeout=None)
                        except Exception as e:
                            # Catch all exceptions including "I/O operation on closed file"
                            error_msg = str(e)
                            
                            # Check if process completed successfully despite the error
                            try:
                                if proc.poll() is None:
                                    proc.wait(timeout=2)
                            except Exception:
                                pass
                            
                            # If return code is 0, operation succeeded despite the exception
                            if proc.returncode == 0:
                                return True, "", ""
                            
                            # Only report error if return code indicates failure
                            if "closed file" in error_msg.lower() or "I/O operation" in error_msg:
                                # This is often a harmless error if the process succeeded
                                if proc.returncode == 0:
                                    return True, "", ""
                                # If it failed, log it
                                self.log(f"Error during command execution: {error_msg}", "error")
                            else:
                                self.log(f"Error during command execution: {error_msg}", "error")
                            
                            self._terminate_process(proc)
                            return False, "", error_msg
                        except subprocess.TimeoutExpired:
                            # This shouldn't happen with timeout=None, but handle it just in case
                            if self.cancel_event.is_set():
                                self._terminate_process(proc)
                                return False, "", "Cancelled"
                            try:
                                proc.communicate()
                            except Exception:
                                pass
                        return proc.returncode == 0, "", ""
                finally:
                    self._unregister_process(proc)
            else:
                # Non-sudo command, run normally with cancellation support
                proc = subprocess.Popen(
                    command if not shell else (command if isinstance(command, str) else " ".join(command)),
                    shell=shell,
                    stdout=subprocess.PIPE if capture else None,
                    stderr=subprocess.PIPE if capture else None,
                    text=capture,
                    env=env if env else os.environ.copy(),
                    preexec_fn=os.setsid
                )
                self._register_process(proc)
                try:
                    if capture:
                        stdout_acc = ""
                        stderr_acc = ""
                        while True:
                            try:
                                out, err = proc.communicate(timeout=0.1)
                                stdout_acc += out or ""
                                stderr_acc += err or ""
                                break
                            except subprocess.TimeoutExpired:
                                if self.cancel_event.is_set():
                                    self._terminate_process(proc)
                                    return False, stdout_acc, "Cancelled"
                                continue
                        success = proc.returncode == 0
                        return success, stdout_acc, stderr_acc
                    else:
                        while True:
                            if self.cancel_event.is_set():
                                self._terminate_process(proc)
                                return False, "", "Cancelled"
                            if proc.poll() is not None:
                                break
                            time.sleep(0.1)
                        return proc.returncode == 0, "", ""
                finally:
                    self._unregister_process(proc)
        except Exception as e:
            return False, "", str(e)
    
    def run_command_streaming(self, command, env=None, progress_callback=None):
        """Execute command and stream output to log in real-time, cancellable.
        Also stores the full streamed text in self._last_stream_output_text for post-run heuristics."""
        self._last_stream_output_text = ""
        try:
            if isinstance(command, str):
                command = command.split()
            
            # Set up environment for non-interactive operation
            if env is None:
                env = os.environ.copy()
            
            # Force non-interactive mode for various tools
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            env['NEEDRESTART_MODE'] = 'a'  # Auto-restart services without asking
            env['DEBIAN_PRIORITY'] = 'critical'
            env['APT_LISTCHANGES_FRONTEND'] = 'none'
            env['LANG'] = 'C'  # Use C locale to avoid encoding issues
            env['LC_ALL'] = 'C'
            
            # Unset SUDO_ASKPASS if this is a sudo command
            is_sudo = isinstance(command, list) and len(command) > 0 and command[0] == "sudo"
            if is_sudo:
                env.pop('SUDO_ASKPASS', None)
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                preexec_fn=os.setsid
            )
            self._register_process(process)
            
            # Stream output line by line
            buffer = []
            for line in iter(process.stdout.readline, ''):
                if self.cancel_event.is_set():
                    self._terminate_process(process)
                    self._last_stream_output_text = "".join(buffer)
                    return False
                if line:
                    # Clean up the line and log it
                    line = line.rstrip()
                    if line:
                        buffer.append(line + "\n")
                        # Show important progress messages
                        line_lower = line.lower()
                        # Always show progress-related messages
                        if any(keyword in line_lower for keyword in [
                            'progress', 'downloading', 'installing', 'extracting', 
                            'configuring', 'executing', 'running', 'done', 'complete',
                            'success', 'error', 'failed', 'warning', '%', 'mb', 'kb'
                        ]):
                            self.log(f"  {line}", "info")
                            
                            # Try to extract progress percentage if callback provided
                            if progress_callback:
                                import re
                                percent_match = re.search(r'(\d+)\s*%', line, re.IGNORECASE)
                                if percent_match:
                                    try:
                                        percent = int(percent_match.group(1))
                                        progress_callback(percent / 100.0)
                                    except (ValueError, TypeError):
                                        pass
                        # Filter out very verbose Wine debug messages but keep important ones
                        elif not any(skip in line_lower for skip in [
                            'fixme:', 'trace:', 'debug:'
                        ]):
                            # Show other non-debug messages
                            self.log(f"  {line}", "info")
            
            process.wait()
            self._last_stream_output_text = "".join(buffer)
            return process.returncode == 0
        except Exception as e:
            self.log(f"Error running command: {e}", "error")
            return False
        finally:
            try:
                self._unregister_process(process)
            except Exception:
                pass

    def _to_windows_path(self, unix_path, env=None):
        """Convert a UNIX path to a Windows path for Wine 'start' using winepath.
        Falls back to Z: drive mapping if winepath is unavailable."""
        try:
            winepath_bin = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winepath"
            if winepath_bin.exists():
                success, stdout, _ = self.run_command([str(winepath_bin), "-w", str(unix_path)], check=False, env=env, capture=True)
                if success and stdout:
                    return stdout.strip().splitlines()[-1]
        except Exception:
            pass
        # Fallback: Z: mapping
        p = str(unix_path)
        if p.startswith("/"):
            win = "Z:" + p
        else:
            win = p
        return win.replace("/", "\\")

    def _has_installer_activity(self, installer_file: Path) -> bool:
        """Heuristics to detect installer activity:
        - Check for Wine processes referencing installer/common names
        - If wmctrl is available, check for visible windows with class/name containing wine/setup/installer
        """
        try:
            # Process-based heuristic
            patterns = [installer_file.name.lower(), "setup", "msiexec", "install", ".msi", ".exe"]
            success, stdout, _ = self.run_command(["ps", "-eo", "pid,command"], check=False, capture=True)
            if success and stdout:
                text = stdout.lower()
                if ("wine" in text or "wineserver" in text) and any(pat in text for pat in patterns):
                    return True
            # Window-based heuristic (wmctrl)
            wmctrl = shutil.which("wmctrl")
            if wmctrl:
                ok, wout, _ = self.run_command([wmctrl, "-lx"], check=False, capture=True)
                if ok and wout:
                    w = wout.lower()
                    # Examples: 'wine.wine explorer.exe', 'setup.exe', 'affinity'
                    if "wine" in w and any(pat in w for pat in patterns):
                        return True
        except Exception:
            pass
        return False

    def _run_installer_and_capture(self, installer_file: Path, env: dict, label: str = "installer"):
        """Run a Windows installer under Wine, stream logs, and wait robustly until it exits.
        Strategy:
        1) Try 'wine start /wait /unix <file>'
        2) If it exits too quickly or returns non-zero with no activity, try 'wine <file>'
        3) After launch, wait on 'wineserver -w' to ensure child processes finish (cancellable)
        """
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        attempts = [
            [str(wine), "start", "/wait", "/unix", str(installer_file)],
            [str(wine), str(installer_file)],
        ]
        for idx, cmd in enumerate(attempts, start=1):
            try:
                cmd_str = " ".join(shlex.quote(c) for c in cmd)
                self.log(f"Running ({label}) attempt {idx}: {cmd_str}", "info")
                t0 = time.time()
                ok = self.run_command_streaming(cmd, env=env)
                dt = time.time() - t0
                # If it "succeeded" unrealistically fast, poll briefly for activity or window
                if ok and dt < 5.0:
                    self.log(f"{label.capitalize()} attempt {idx} returned quickly ({dt:.2f}s). Polling for activity...", "warning")
                    for _ in range(30):  # ~3s
                        if self.check_cancelled():
                            return False
                        if self._has_installer_activity(installer_file):
                            break
                        time.sleep(0.1)
                    else:
                        ok = False
                # Also verify there was some wine activity (best-effort heuristic)
                if ok and not self._has_installer_activity(installer_file):
                    # As a last signal, check stream output for obvious errors
                    txt = (self._last_stream_output_text or "").lower()
                    error_markers = ["err:", "cannot find", "bad exe", "failed", "error:", "no such file", "unable to load"]
                    if any(m in txt for m in error_markers):
                        ok = False
                if ok:
                    self.log("Waiting for Wine processes to finish (wineserver -w)...", "info")
                    # Extended wait; cancellable via run_command loop
                    env_wait = env.copy() if env else os.environ.copy()
                    env_wait["WINEPREFIX"] = self.directory
                    self.run_command(["wineserver", "-w"], check=False, capture=False, env=env_wait)
                    return True
                if self.check_cancelled():
                    return False
                self.log(f"{label.capitalize()} attempt {idx} did not run (ok={ok}, dt={dt:.2f}s). Trying fallback...", "warning")
            except Exception as e:
                self.log(f"Error launching {label} attempt {idx}: {e}", "error")
        return False
    
    def run_command_interactive(self, command, env=None):
        """Execute command and handle interactive prompts via GUI, cancellable."""
        try:
            if isinstance(command, str):
                command = command.split()
            
            # Set up environment for non-interactive operation
            if env is None:
                env = os.environ.copy()
            
            # Force non-interactive mode for various tools
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            env['NEEDRESTART_MODE'] = 'a'
            env['DEBIAN_PRIORITY'] = 'critical'
            env['APT_LISTCHANGES_FRONTEND'] = 'none'
            env['LANG'] = 'C'
            env['LC_ALL'] = 'C'
            
            # Check if this is a sudo command
            is_sudo = isinstance(command, list) and len(command) > 0 and command[0] == "sudo"
            
            # Unset SUDO_ASKPASS to force sudo to read password from stdin via -S flag
            # This prevents errors when askpass programs (like ksshaskpass) don't exist
            if is_sudo:
                env.pop('SUDO_ASKPASS', None)
            
            if is_sudo:
                # Get password if needed
                password = self.get_sudo_password()
                if password is None:
                    self.log("Authentication cancelled by user", "warning")
                    return False, "", "Authentication cancelled"
                
                # Validate password if not already validated
                if not self.sudo_password_validated:
                    if not self.validate_sudo_password(password):
                        self.log("Authentication failed", "error")
                        return False, "", "Authentication failed"
                
                # Add -S flag if not present
                # Create a copy to avoid modifying the original
                command = list(command)
                if len(command) > 1:
                    if command[1] != "-S":
                        # Remove -S if it exists elsewhere (safely)
                        while "-S" in command:
                            command.remove("-S")
                        # Insert -S right after "sudo"
                        command.insert(1, "-S")
                else:
                    # Only "sudo" in command, add -S
                    command.append("-S")
            
            # Start process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                preexec_fn=os.setsid
            )
            self._register_process(process)
            
            # If sudo, send password first
            if is_sudo and self.sudo_password:
                try:
                    process.stdin.write(f"{self.sudo_password}\n")
                    process.stdin.flush()
                except Exception:
                    pass
            
            # Read output and detect prompts
            output_lines = []
            error_lines = []
            
            import select
            
            while True:
                if self.cancel_event.is_set():
                    self._terminate_process(process)
                    return False, "", "Cancelled"
                # Check if process has finished
                if process.poll() is not None:
                    # Read any remaining output
                    remaining_out = process.stdout.read()
                    remaining_err = process.stderr.read()
                    if remaining_out:
                        output_lines.append(remaining_out)
                    if remaining_err:
                        error_lines.append(remaining_err)
                    break
                
                # Try to read from stdout with timeout
                try:
                    # Use select to check if data is available (Unix-like systems)
                    import sys
                    if hasattr(select, 'select'):
                        readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                        
                        for stream in readable:
                            line = stream.readline()
                            if line:
                                if stream == process.stdout:
                                    output_lines.append(line)
                                    self.log(f"  {line.rstrip()}", "info")
                                else:
                                    error_lines.append(line)
                                
                                # Detect interactive prompts
                                line_lower = line.lower()
                                if any(pattern in line_lower for pattern in [
                                    "overwrite?", "(y/n)", "[y/n]", "yes/no",
                                    "continue?", "proceed?", "replace?"
                                ]):
                                    # Interactive prompt detected!
                                    self.log(f"Interactive prompt detected: {line.rstrip()}", "warning")
                                    
                                    # Extract default response if present
                                    default = ""
                                    if "(y/n)" in line_lower:
                                        # Check which is capitalized
                                        if "(Y/n)" in line:
                                            default = "y"
                                        elif "(y/N)" in line:
                                            default = "n"
                                    
                                    # Get user response via GUI
                                    response = self.get_interactive_response(line.rstrip(), default)
                                    
                                    # Send response to process
                                    if process.stdin:
                                        process.stdin.write(response)
                                        process.stdin.flush()
                except Exception as e:
                    self.log(f"Error reading process output: {e}", "warning")
                    time.sleep(0.1)
            
            # Get return code
            return_code = process.wait()
            
            stdout_text = "".join(output_lines)
            stderr_text = "".join(error_lines)
            
            return return_code == 0, stdout_text, stderr_text
            
        except Exception as e:
            self.log(f"Error in interactive command: {e}", "error")
            return False, "", str(e)
        finally:
            try:
                self._unregister_process(process)
            except Exception:
                pass
    
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
            
            # Normalize "pika" to "pikaos" if detected
            if self.distro == "pika":
                self.distro = "pikaos"
            
            # Normalize "pop" to "pop" if detected
            if self.distro == "pop":
                self.distro = "pop"
            
            return True
        except Exception as e:
            self.log(f"Error detecting distribution: {e}", "error")
            return False
    
    def download_file(self, url, output_path, description=""):
        """Download file with progress tracking"""
        try:
            # Check if cancelled before starting
            if self.check_cancelled():
                return False
            
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
                        # Check for cancellation during download
                        if self.check_cancelled():
                            self.log(f"Download of {description} cancelled", "warning")
                            return False
                        
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
        self.start_operation("One-Click Full Setup")
        
        # Ensure patcher files are available
        self.ensure_patcher_files()
        
        # Step 1: Detect distribution
        self.update_progress_text("Step 1/4: Detecting Linux distribution...")
        self.update_progress(0.05)
        
        if self.check_cancelled():
            return
        
        if not self.detect_distro():
            self.log("Failed to detect distribution. Cannot continue.", "error")
            self.update_progress_text("Ready")
            self.end_operation()
            return
        
        self.log(f"Detected distribution: {self.distro} {self.distro_version or ''}", "success")
        
        if self.check_cancelled():
            return
        
        # Step 2: Check and install dependencies
        self.update_progress_text("Step 2/4: Checking and installing system dependencies...")
        self.update_progress(0.15)
        
        if self.check_cancelled():
            return
        
        if not self.check_dependencies():
            self.log("Dependency check failed. Please resolve issues and try again.", "error")
            self.update_progress_text("Ready")
            self.end_operation()
            
            # Show retry dialog
            reply = self.show_question_dialog(
                "Dependency Check Failed",
                "Dependency check failed. Please resolve issues and try again.\n\n"
                "Would you like to retry the dependency check?",
                ["Yes", "No"]
            )
            
            if reply == "Yes":
                # Retry dependency check
                return self._one_click_setup_thread()
            else:
                self.end_operation()
                return
        
        if self.check_cancelled():
            return
        
        # Step 3: Setup Wine environment (this includes winetricks dependencies via configure_wine)
        self.update_progress_text("Step 3/4: Setting up Wine environment...")
        self.update_progress(0.40)
        
        if self.check_cancelled():
            return
        
        self.setup_wine()
        
        if self.check_cancelled():
            return
        
        # Step 4: Install Affinity v3 settings to enable settings saving
        self.update_progress_text("Step 4/4: Installing Affinity v3 settings...")
        self.update_progress(0.90)
        
        if self.check_cancelled():
            return
        
        self.log("Installing Affinity v3 settings files...", "info")
        self._install_affinity_settings_thread()
        
        if self.check_cancelled():
            return
        
        # Complete!
        self.update_progress(1.0)
        self.update_progress_text("Setup Complete!")
        self.log("\n✓ Full setup completed!", "success")
        self.log("You can now install Affinity applications using the buttons above.", "info")
        
        # End operation
        self.end_operation()
        
        # Refresh installation status to update button states
        QTimer.singleShot(100, self.check_installation_status)
        
        # Ask if user wants to install an Affinity app
        self.prompt_affinity_install_signal.emit()
    
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
                    self.install_application_signal.emit(app_code)
    
    def install_application(self, app_code):
        """Install an Affinity application - asks user if they want to download or provide their own exe"""
        app_names = {
            "Add": "Affinity (Unified)",
            "Photo": "Affinity Photo",
            "Designer": "Affinity Designer",
            "Publisher": "Affinity Publisher"
        }
        display_name = app_names.get(app_code, "Affinity")
        
        # Check if Wine is set up
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        # Ask user if they want to download or provide their own exe
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Install {display_name}")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        label = QLabel(f"How would you like to get the {display_name} installer?")
        layout.addWidget(label)
        
        button_group = QButtonGroup()
        download_radio = QRadioButton("Download from Affinity Studio (automatic)")
        download_radio.setChecked(True)
        custom_radio = QRadioButton("Provide my own installer file (.exe)")
        
        button_group.addButton(download_radio, 0)
        button_group.addButton(custom_radio, 1)
        
        layout.addWidget(download_radio)
        layout.addWidget(custom_radio)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            checked_id = button_group.checkedId()
            installer_path = None
            
            if checked_id == 0:  # Download
                # Download the installer in background, then install
                self.log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log(f"Downloading {display_name} Installer", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                
                download_url = "https://downloads.affinity.studio/Affinity%20x64.exe"
                download_dir = Path.home() / ".cache" / "affinity-installer"
                download_dir.mkdir(parents=True, exist_ok=True)
                installer_path = download_dir / "Affinity-x64.exe"
                
                self.start_operation(f"Install {display_name}")
                threading.Thread(
                    target=self._download_then_install,
                    args=(app_code, display_name, download_url, str(installer_path)),
                    daemon=True
                ).start()
                return
                
            else:  # Provide own file
                # Open file dialog to select .exe
                self.log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log(f"Custom Installer for {display_name}", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                self.log("Please select the installer .exe file...", "info")
                
                installer_path, _ = QFileDialog.getOpenFileName(
                    self,
                    f"Select {display_name} Installer",
                    "",
                    "Executable files (*.exe);;All files (*.*)"
                )
                
                if not installer_path:
                    self.log("Installation cancelled.", "warning")
                    return
                # QFileDialog returns a string, but we'll normalize it
                installer_path = Path(installer_path)
            
            # Verify file exists and convert to string for run_installation
            installer_path_str = str(installer_path)
            if not Path(installer_path_str).exists():
                self.log(f"Installer file not found: {installer_path_str}", "error")
                return
            
            # Start operation and installation in background thread
            self.start_operation(f"Install {display_name}")
            threading.Thread(
                target=self._run_installation_entry,
                args=(app_code, installer_path_str),
                daemon=True
            ).start()
    
    def _download_then_install(self, app_code, display_name, download_url, installer_path_str):
        """Download installer then run installation (runs in background)."""
        try:
            self.log(f"Downloading from: {download_url}", "info")
            if not self.download_file(download_url, installer_path_str, f"{display_name} installer"):
                self.log("Download failed. Please try providing your own installer file.", "error")
                self.show_message(
                    "Download Failed",
                    "Failed to download the installer.\n\nYou can download it manually from:\nhttps://downloads.affinity.studio/Affinity%20x64.exe\n\nThen use 'Provide my own installer file' option.",
                    "error"
                )
                # End the operation because run_installation won't be called
                self.end_operation()
                return
            self.log(f"Download completed: {installer_path_str}", "success")
            # Proceed to install (will end operation in wrapper)
            self._run_installation_entry(app_code, installer_path_str)
        except Exception as e:
            self.log(f"Error during download+install: {e}", "error")
            self.end_operation()

    def check_dependencies(self):
        """Check and install dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Dependency Verification", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        self.update_progress_text("Checking dependencies...")
        self.update_progress(0.0)
        
        # Show unsupported warning
        if self.distro in ["ubuntu", "linuxmint", "zorin"]:
            self.show_unsupported_warning()
        
        missing = []
        deps = ["wine", "winetricks", "wget", "curl", "tar", "jq"]
        total_checks = len(deps) + 3  # +3 for archive tools, zstd, and dotnet
        
        for idx, dep in enumerate(deps):
            progress = (idx + 1) / total_checks * 0.5  # Use first 50% for checking
            self.update_progress(progress)
            self.update_progress_text(f"Checking {dep}...")
            
            if self.check_command(dep):
                self.log(f"{dep} is installed", "success")
            else:
                self.log(f"{dep} is not installed", "error")
                missing.append(dep)
        
        # Check for either 7z or unzip (both can extract archives)
        progress = (len(deps) + 1) / total_checks * 0.5
        self.update_progress(progress)
        self.update_progress_text("Checking archive tools...")
        
        if not self.check_command("7z") and not self.check_command("unzip"):
            self.log("Neither 7z nor unzip is installed (at least one is required)", "error")
            missing.append("7z or unzip")
        else:
            if self.check_command("7z"):
                self.log("7z is installed", "success")
            else:
                self.log("unzip is installed (will be used instead of 7z)", "success")
        
        # Check zstd
        progress = (len(deps) + 2) / total_checks * 0.5
        self.update_progress(progress)
        self.update_progress_text("Checking zstd...")
        
        if not (self.check_command("unzstd") or self.check_command("zstd")):
            self.log("zstd or unzstd is not installed", "error")
            missing.append("zstd")
        else:
            self.log("zstd support is available", "success")
        
        # Check .NET SDK (optional but recommended for Affinity v3 settings fix)
        progress = (len(deps) + 3) / total_checks * 0.5
        self.update_progress(progress)
        self.update_progress_text("Checking .NET SDK...")
        
        if not self.check_dotnet_sdk():
            self.log(".NET SDK is not installed (optional - needed for Affinity v3 settings fix)", "warning")
            missing.append("dotnet-sdk")
        else:
            self.log(".NET SDK is installed", "success")
        
        # Handle unsupported distributions - show warning and allow retry
        if self.distro in ["ubuntu", "linuxmint", "pop", "zorin"]:
            if missing:
                self.log("\n" + "="*80, "error")
                self.log("⚠️  WARNING: UNSUPPORTED DISTRIBUTION", "error")
                self.log("="*80, "error")
                self.log("\nMissing dependencies detected.", "error")
                self.log("This script will NOT auto-install for unsupported distributions.", "error")
                self.log("Please install the required dependencies manually.", "warning")
                self.log(f"Missing: {', '.join(missing)}", "warning")
                
                # Show dialog asking user to install and retry
                reply = self.show_question_dialog(
                    "Unsupported Distribution - Missing Dependencies",
                    f"⚠️  WARNING: UNSUPPORTED DISTRIBUTION\n\n"
                    f"Missing dependencies: {', '.join(missing)}\n\n"
                    f"This script will NOT auto-install for unsupported distributions.\n"
                    f"Please install the required dependencies manually.\n\n"
                    f"Click 'Retry' after installing dependencies, or 'Cancel' to exit.",
                    ["Retry", "Cancel"]
                )
                
                if reply == "Retry":
                    # Re-check dependencies
                    return self.check_dependencies()
                else:
                    return False
            else:
                self.log("\nAll dependencies installed, but you are on an unsupported distribution.", "warning")
                self.log("No support will be provided if issues arise.", "warning")
        
        # Install missing dependencies (only for supported distributions)
        if missing and self.distro not in ["ubuntu", "linuxmint", "pop", "zorin"]:
            self.log(f"\nInstalling missing dependencies: {', '.join(missing)}", "info")
            self.update_progress_text(f"Installing {len(missing)} missing packages...")
            self.update_progress(0.5)  # Start second half of progress
            
            # Request password before attempting installation
            self.log("Administrator privileges required for package installation.", "info")
            self.update_progress_text("Requesting administrator password...")
            
            # Try to get and validate password (with retries)
            max_password_attempts = 3
            password_valid = False
            
            for password_attempt in range(max_password_attempts):
                password = self.get_sudo_password()
                if password is None:
                    self.log("Password entry cancelled. Cannot install dependencies.", "error")
                    self.update_progress_text("Dependency installation cancelled")
                    return False
                
                # Validate password before proceeding
                if not self.sudo_password_validated:
                    self.log(f"Validating password... (attempt {password_attempt + 1}/{max_password_attempts})", "info")
                    if self.validate_sudo_password(password):
                        self.log("Password validated successfully.", "success")
                        password_valid = True
                        break
                    else:
                        if password_attempt < max_password_attempts - 1:
                            self.log("Password validation failed. Please try again.", "error")
                            # Clear the password to force a new dialog on next get_sudo_password call
                            self.sudo_password = None
                            self.sudo_password_validated = False
                            # Wait a moment for user to see the error message
                            time.sleep(1)
                        else:
                            self.log("Password validation failed after multiple attempts.", "error")
                            return False
                else:
                    # Password already validated
                    password_valid = True
                    break
            
            if not password_valid:
                self.log("Could not validate password. Cannot install dependencies.", "error")
                self.update_progress_text("Dependency installation cancelled")
                return False
            
            if not self.install_dependencies():
                self.update_progress_text("Dependency installation failed")
                return False
        
        self.update_progress(1.0)
        self.update_progress_text("All dependencies installed")
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
        if self.distro == "pop":
            return self.install_popos_dependencies()
        
        commands = {
            "arch": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "cachyos": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "endeavouros": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "xerolinux": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "fedora": ["sudo", "dnf", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "p7zip-plugins", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "nobara": ["sudo", "dnf", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "p7zip-plugins", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "opensuse-tumbleweed": ["sudo", "zypper", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"],
            "opensuse-leap": ["sudo", "zypper", "install", "-y", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd", "dotnet-sdk-8.0"]
        }
        
        if self.distro in commands:
            self.log(f"Installing dependencies for {self.distro}...", "info")
            self.update_progress_text(f"Installing packages for {self.distro}...")
            self.update_progress(0.6)
            
            success, stdout, stderr = self.run_command(commands[self.distro])
            
            if success:
                self.update_progress(1.0)
                self.update_progress_text("Dependencies installed")
                self.log("Dependencies installed successfully", "success")
                return True
            else:
                self.log(f"Failed to install dependencies: {stderr}", "error")
                
                # Show retry dialog
                reply = self.show_question_dialog(
                    "Dependency Installation Failed",
                    f"Failed to install dependencies:\n{stderr}\n\n"
                    "Would you like to retry the installation?",
                    ["Yes", "No"]
                )
                
                if reply == "Yes":
                    # Retry installation
                    return self.install_dependencies()
                else:
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
        
        # Total steps: keyrings, gpg key, i386, repo, apt update, wine install, deps install = 7 steps
        total_steps = 7
        current_step = 0
        
        # Create keyrings directory
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Creating keyrings directory...")
        self.update_progress(current_step / total_steps)
        self.log("Creating APT keyrings directory...", "info")
        success, _, _ = self.run_command(["sudo", "mkdir", "-pm755", "/etc/apt/keyrings"])
        if not success:
            self.log("Failed to create keyrings directory", "error")
            return False
        
        # Add GPG key
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding WineHQ GPG key...")
        self.update_progress(current_step / total_steps)
        self.log("Adding WineHQ GPG key...", "info")
        success, stdout, _ = self.run_command(["wget", "-O", "-", "https://dl.winehq.org/wine-builds/winehq.key"])
        if success:
            # Get sudo password for GPG operation
            password = self.get_sudo_password()
            if password is None:
                self.log("Authentication cancelled by user", "error")
                return False
            
            # Validate password if not already validated
            if not self.sudo_password_validated:
                if not self.validate_sudo_password(password):
                    self.log("Authentication failed", "error")
                    return False
            
            # Run GPG command with sudo
            gpg_proc = subprocess.Popen(
                ["sudo", "-S", "gpg", "--dearmor", "-o", "/etc/apt/keyrings/winehq-archive.key", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Send password first, then the key data
            gpg_input = f"{self.sudo_password}\n" + stdout
            gpg_stdout, gpg_stderr = gpg_proc.communicate(input=gpg_input)
            
            if gpg_proc.returncode == 0:
                self.log("WineHQ GPG key added", "success")
            else:
                self.log(f"Failed to add GPG key: {gpg_stderr}", "error")
                return False
        else:
            self.log("Failed to download GPG key", "error")
            return False
        
        # Add i386 architecture
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding i386 architecture...")
        self.update_progress(current_step / total_steps)
        self.log("Adding i386 architecture...", "info")
        success, _, _ = self.run_command(["sudo", "dpkg", "--add-architecture", "i386"])
        if not success:
            self.log("Failed to add i386 architecture", "error")
            return False
        
        # Add repository
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding WineHQ repository...")
        self.update_progress(current_step / total_steps)
        self.log("Adding WineHQ repository...", "info")
        # Remove existing file first to avoid overwrite prompt
        repo_file = Path("/etc/apt/sources.list.d/winehq-forky.sources")
        if repo_file.exists():
            self.run_command(["sudo", "rm", "-f", str(repo_file)], check=False)
        
        success, _, _ = self.run_command([
            "sudo", "wget", "-P", "/etc/apt/sources.list.d/",
            "https://dl.winehq.org/wine-builds/debian/dists/forky/winehq-forky.sources"
        ])
        if not success:
            self.log("Failed to add repository", "error")
            return False
        
        # Update package lists
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Updating package lists...")
        self.update_progress(current_step / total_steps)
        self.log("Updating package lists...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "update"])
        if not success:
            self.log("Failed to update package lists", "error")
            return False
        
        # Install WineHQ staging
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Installing WineHQ staging...")
        self.update_progress(current_step / total_steps)
        self.log("Installing WineHQ staging...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "install", "--install-recommends", "-y", "winehq-staging"])
        if not success:
            self.log("Failed to install WineHQ staging", "error")
            return False
        
        # Install remaining dependencies
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Installing remaining dependencies...")
        self.update_progress(current_step / total_steps)
        self.log("Installing remaining dependencies...", "info")
        success, _, _ = self.run_command([
            "sudo", "apt", "install", "-y", "winetricks", "wget", "curl", "p7zip-full", "tar", "jq", "zstd"
        ])
        if not success:
            self.log("Failed to install remaining dependencies", "error")
            return False
        
        self.update_progress(1.0)
        self.update_progress_text("PikaOS dependencies installed")
        self.log("All dependencies installed for PikaOS", "success")
        return True
    
    def install_popos_dependencies(self):
        """Install Pop!_OS dependencies with WineHQ staging"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Pop!_OS Special Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log("Pop!_OS's built-in Wine has compatibility issues.", "warning")
        self.log("Setting up WineHQ staging from Ubuntu...\n", "info")
        
        # Total steps: keyrings, gpg key, i386, repo, apt update, wine install, deps install = 7 steps
        total_steps = 7
        current_step = 0
        
        # Create keyrings directory
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Creating keyrings directory...")
        self.update_progress(current_step / total_steps)
        self.log("Creating APT keyrings directory...", "info")
        success, _, _ = self.run_command(["sudo", "mkdir", "-pm755", "/etc/apt/keyrings"])
        if not success:
            self.log("Failed to create keyrings directory", "error")
            return False
        
        # Add GPG key
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding WineHQ GPG key...")
        self.update_progress(current_step / total_steps)
        self.log("Adding WineHQ GPG key...", "info")
        success, stdout, _ = self.run_command(["wget", "-O", "-", "https://dl.winehq.org/wine-builds/winehq.key"])
        if success:
            # Get sudo password for GPG operation
            password = self.get_sudo_password()
            if password is None:
                self.log("Authentication cancelled by user", "error")
                return False
            
            # Validate password if not already validated
            if not self.sudo_password_validated:
                if not self.validate_sudo_password(password):
                    self.log("Authentication failed", "error")
                    return False
            
            # Run GPG command with sudo
            gpg_proc = subprocess.Popen(
                ["sudo", "-S", "gpg", "--dearmor", "-o", "/etc/apt/keyrings/winehq-archive.key", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Send password first, then the key data
            gpg_input = f"{self.sudo_password}\n" + stdout
            gpg_stdout, gpg_stderr = gpg_proc.communicate(input=gpg_input)
            
            if gpg_proc.returncode == 0:
                self.log("WineHQ GPG key added", "success")
            else:
                self.log(f"Failed to add GPG key: {gpg_stderr}", "error")
                return False
        else:
            self.log("Failed to download GPG key", "error")
            return False
        
        # Add i386 architecture
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding i386 architecture...")
        self.update_progress(current_step / total_steps)
        self.log("Adding i386 architecture...", "info")
        success, _, _ = self.run_command(["sudo", "dpkg", "--add-architecture", "i386"])
        if not success:
            self.log("Failed to add i386 architecture", "error")
            return False
        
        # Add repository
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Adding WineHQ repository...")
        self.update_progress(current_step / total_steps)
        self.log("Adding WineHQ repository...", "info")
        # Get Ubuntu version codename
        codename = "jammy"
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("VERSION_CODENAME="):
                        codename = line.split("=")[1].strip()
        except (IOError, FileNotFoundError):
            pass # Default to jammy
            
        # Remove existing file first to avoid overwrite prompt
        repo_file = Path(f"/etc/apt/sources.list.d/winehq-{codename}.sources")
        if repo_file.exists():
            self.run_command(["sudo", "rm", "-f", str(repo_file)], check=False)
        
        success, _, _ = self.run_command([
            "sudo", "wget", "-P", "/etc/apt/sources.list.d/",
            f"https://dl.winehq.org/wine-builds/ubuntu/dists/{codename}/winehq-{codename}.sources"
        ])
        if not success:
            self.log("Failed to add repository", "error")
            return False
        
        # Update package lists
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Updating package lists...")
        self.update_progress(current_step / total_steps)
        self.log("Updating package lists...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "update"])
        if not success:
            self.log("Failed to update package lists", "error")
            return False
        
        # Install WineHQ staging
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Installing WineHQ staging...")
        self.update_progress(current_step / total_steps)
        self.log("Installing WineHQ staging...", "info")
        success, _, _ = self.run_command(["sudo", "apt", "install", "--install-recommends", "-y", "winehq-staging"])
        if not success:
            self.log("Failed to install WineHQ staging", "error")
            return False
        
        # Install remaining dependencies
        current_step += 1
        self.update_progress_text(f"Step {current_step}/{total_steps}: Installing remaining dependencies...")
        self.update_progress(current_step / total_steps)
        self.log("Installing remaining dependencies...", "info")
        success, _, _ = self.run_command([
            "sudo", "apt", "install", "-y", "winetricks", "wget", "curl", "p7zip-full", "tar", "jq", "zstd", "dotnet-sdk-8.0"
        ])
        if not success:
            self.log("Failed to install remaining dependencies", "error")
            self.log("Note: dotnet-sdk-8.0 may require Microsoft's repository. You can install it manually if needed.", "warning")
            return False
        
        self.update_progress(1.0)
        self.update_progress_text("Pop!_OS dependencies installed")
        self.log("All dependencies installed for Pop!_OS", "success")
        return True
    
    def setup_wine(self):
        """Setup Wine environment"""
        self.start_operation("Setting up Wine environment")
        
        try:
            # Check if cancelled at start
            if self.check_cancelled():
                return False
            
            self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.log("Wine Binary Setup", "info")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
            # Stop Wine processes
            self.update_progress_text("Preparing Wine environment...")
            self.update_progress(0.0)
            self.log("Stopping Wine processes...", "info")
            self.run_command(["wineserver", "-k"], check=False)
            
            if self.check_cancelled():
                return False
            
            # Create directory
            self.update_progress_text("Creating installation directory...")
            self.update_progress(0.05)
            Path(self.directory).mkdir(parents=True, exist_ok=True)
            self.log("Installation directory created", "success")
            
            if self.check_cancelled():
                return False
            
            # Download Wine binary
            wine_url = "https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
            wine_file = Path(self.directory) / "ElementalWarriorWine-x86_64.tar.gz"
            
            self.update_progress_text("Downloading Wine binary...")
            self.update_progress(0.10)
            self.log("Downloading Wine binary...", "info")
            if not self.download_file(wine_url, str(wine_file), "Wine binaries"):
                self.log("Failed to download Wine binary", "error")
                self.update_progress_text("Ready")
                return False
            
            if self.check_cancelled():
                return False
            
            # Extract Wine
            self.update_progress_text("Extracting Wine binary...")
            self.update_progress(0.50)
            self.log("Extracting Wine binary...", "info")
            try:
                with tarfile.open(wine_file, "r:gz") as tar:
                    tar.extractall(self.directory, filter='data')
                wine_file.unlink()
                self.log("Wine binary extracted", "success")
            except Exception as e:
                self.log(f"Failed to extract Wine: {e}", "error")
                self.update_progress_text("Ready")
                return False
            
            if self.check_cancelled():
                return False
            
            # Find and link Wine directory
            self.update_progress(0.55)
            wine_dir = next(Path(self.directory).glob("ElementalWarriorWine*"), None)
            if wine_dir and wine_dir != Path(self.directory) / "ElementalWarriorWine":
                target = Path(self.directory) / "ElementalWarriorWine"
                if target.exists() or target.is_symlink():
                    target.unlink()
                target.symlink_to(wine_dir)
                self.log("Wine symlink created", "success")
            
            # Verify Wine binary
            self.update_progress(0.60)
            wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            if not wine_binary.exists():
                self.log("Wine binary not found", "error")
                self.update_progress_text("Ready")
                return False
            
            self.log("Wine binary verified", "success")
            
            if self.check_cancelled():
                return False
            
            # Download icons
            self.update_progress_text("Downloading application icons...")
            self.update_progress(0.65)
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
                ("https://raw.githubusercontent.com/seapear/AffinityOnLinux/main/Assets/Icons/Affinity-Canva.svg",
                 icons_dir / "Affinity.svg", "Affinity V3 icon")
            ]
            
            total_icons = len(icons)
            for idx, (url, path, desc) in enumerate(icons):
                if self.check_cancelled():
                    return False
                icon_progress = 0.65 + (idx / total_icons) * 0.05
                self.update_progress(icon_progress)
                if not self.download_file(url, str(path), desc):
                    self.log(f"Warning: {desc} download failed, but continuing...", "warning")
            
            if self.check_cancelled():
                return False
            
            # Setup WinMetadata
            self.update_progress_text("Setting up Windows Metadata...")
            self.update_progress(0.70)
            self.setup_winmetadata()
            
            if self.check_cancelled():
                return False
            
            # Setup vkd3d-proton
            self.update_progress_text("Setting up vkd3d-proton...")
            self.update_progress(0.80)
            self.setup_vkd3d()
            
            if self.check_cancelled():
                return False
            
            # Configure Wine
            self.update_progress_text("Configuring Wine with winetricks...")
            self.update_progress(0.90)
            self.configure_wine()

            if self.check_cancelled():
                return False
                
            self.setup_complete = True
            self.update_progress(1.0)
            self.update_progress_text("Wine setup complete!")
            self.log("\n✓ Wine setup completed!", "success")
            
            # Refresh installation status to update button states
            QTimer.singleShot(100, self.check_installation_status)
            return True
                    
        except Exception as e:
            if not self.check_cancelled():
                self.log(f"Error setting up Wine environment: {e}", "error")
            return False
            
        finally:
            # Make sure to end the operation even if there was an error or cancellation
            if hasattr(self, 'current_operation') and self.current_operation == "Setting up Wine environment":
                self.end_operation()
    
    def setup_winmetadata(self):
        """Download and extract WinMetadata"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Windows Metadata Installation", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        winmetadata_zip = Path(self.directory) / "Winmetadata.zip"
        system32_dir = Path(self.directory) / "drive_c" / "windows" / "system32"
        system32_dir.mkdir(parents=True, exist_ok=True)
        
        self.update_progress_text("Downloading Windows Metadata...")
        self.log("Downloading Windows metadata...", "info")
        if not self.download_file(
            "https://archive.org/download/win-metadata/WinMetadata.zip",
            str(winmetadata_zip),
            "WinMetadata"
        ):
            self.log("Failed to download WinMetadata", "warning")
            return
        
        # Extract WinMetadata
        self.update_progress_text("Extracting Windows Metadata...")
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
        
        self.start_operation("Reinstall WinMetadata")
        threading.Thread(target=self._reinstall_winmetadata_entry, daemon=True).start()
    
    def _reinstall_winmetadata_entry(self):
        """Wrapper: reinstall WinMetadata and end operation."""
        try:
            self._reinstall_winmetadata_thread()
        finally:
            self.end_operation()

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
        
        self.update_progress_text("Downloading vkd3d-proton...")
        self.log("Downloading vkd3d-proton...", "info")
        if not self.download_file(vkd3d_url, str(vkd3d_file), "vkd3d-proton"):
            self.log("Failed to download vkd3d-proton", "error")
            return
        
        # Extract vkd3d-proton
        self.update_progress_text("Extracting vkd3d-proton...")
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
        # Prevent winetricks from showing GUI dialogs
        env["WINETRICKS_GUI"] = "0"
        env["DISPLAY"] = env.get("DISPLAY", ":0")  # Ensure display is set but winetricks won't use GUI
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        components = [
            "dotnet35", "dotnet48", "corefonts", "vcrun2022", 
            "msxml3", "msxml6", "tahoma", "renderer=vulkan"
        ]
        
        self.log("Installing Wine components (this may take several minutes)...", "info")
        total_components = len(components)
        for idx, component in enumerate(components):
            # Calculate base progress for this component (0.0 to 1.0 across all components)
            base_progress = idx / total_components
            component_progress_range = 1.0 / total_components
            
            # Update progress label to show current component
            self.update_progress_text(f"Installing: {component} ({idx + 1}/{total_components})")
            
            self.log(f"Installing {component}... [{idx + 1}/{total_components}]", "info")
            self.log("  (Progress will be shown below)", "info")
            
            # Progress callback that updates based on component progress
            def update_component_progress(percent):
                # percent is 0.0-1.0 for this component
                # Map it to overall progress
                overall_progress = base_progress + (percent * component_progress_range)
                self.update_progress(overall_progress)
            
            # Use streaming to show progress
            self.run_command_streaming(
                ["winetricks", "--unattended", "--verbose", "--force", "--no-isolate", "--optout", component],
                env=env,
                progress_callback=update_component_progress
            )
            
            # Mark this component as complete
            self.update_progress(base_progress + component_progress_range)
        
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
        self.update_progress_text("Ready")
    
    def show_main_menu(self):
        """Display main application menu"""
        self.log("\n✓ Setup complete! Select an application to install:", "success")
        self.update_progress(1.0)
    
    def setup_wine_environment(self):
        """Setup Wine environment only"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Setup Wine Environment", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        threading.Thread(target=self.setup_wine, daemon=True).start()
    
    def install_winetricks_deps(self):
        """Install winetricks dependencies - wrapper for button"""
        self.install_winetricks_dependencies()
    
    def install_system_dependencies(self):
        """Install system dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Installing System Dependencies", "info")
        
        # Start operation and check for cancellation
        self.start_operation("Installing System Dependencies")
        if self.check_cancelled():
            return
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        threading.Thread(target=self._install_system_deps, daemon=True).start()
    
    def _install_system_deps(self):
        """Install system dependencies in thread"""
        if self.distro == "pikaos":
            self.log("Using PikaOS dependency installation...", "info")
            success = self.install_pikaos_dependencies()
            if success:
                # Also install .NET SDK if not already installed
                if not self.check_dotnet_sdk():
                    self.log("Installing .NET SDK...", "info")
                    self.install_dotnet_sdk()
            self.log("System dependencies installation completed" if success else "System dependencies installation failed", "success" if success else "error")
            self.end_operation()
            return
        
        if not self.distro:
            self.detect_distro()
        
        self.log(f"Installing dependencies for {self.distro}...", "info")
        success = self.install_dependencies()
        
        # After installing main dependencies, check and install .NET SDK if missing
        # (it should be included in install_dependencies, but check anyway)
        if success:
            if not self.check_dotnet_sdk():
                self.log(".NET SDK not found in installed packages. Installing separately...", "info")
                self.install_dotnet_sdk()
            else:
                self.log(".NET SDK is already installed", "success")
        
        self.log("System dependencies installation completed" if success else "System dependencies installation failed", "success" if success else "error")
        self.end_operation()
        return success
    
    def install_winetricks_dependencies(self):
        """Install winetricks dependencies"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Installing Winetricks Dependencies", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Start operation and check for cancellation
        self.start_operation("Installing Winetricks Dependencies")
        if self.check_cancelled():
            return
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please wait for Wine setup to complete.", "error")
            QMessageBox.warning(self, "Wine Not Ready", "Wine setup must complete before installing winetricks dependencies.")
            self.end_operation()
            return
        
        threading.Thread(target=self._install_winetricks_deps, daemon=True).start()
    
    def _install_winetricks_deps(self):
        """Install winetricks dependencies in thread"""
        try:
            if self.check_cancelled():
                return
                
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            # Prevent winetricks from showing GUI dialogs
            env["WINETRICKS_GUI"] = "0"
            env["DISPLAY"] = env.get("DISPLAY", ":0")  # Ensure display is set but winetricks won't use GUI
            
            components = [
                ("dotnet35", ".NET Framework 3.5"),
                ("dotnet48", ".NET Framework 4.8"),
                ("corefonts", "Windows Core Fonts"),
                ("vcrun2022", "Visual C++ Redistributables 2022"),
                ("msxml3", "MSXML 3.0"),
                ("msxml6", "MSXML 6.0"),
                ("tahoma", "Tahoma Font"),
                ("renderer=vulkan", "Vulkan Renderer")
            ]
        except Exception as e:
            self.log(f"Error in winetricks dependencies installation: {str(e)}", "error")
            self.log("Please check the logs and try again.", "error")
            self.end_operation()
            return
        
        self.log("Installing Wine components (this may take several minutes)...", "info")
        
        total_components = len(components)
        for idx, (component, description) in enumerate(components):
            # Calculate base progress for this component (0.0 to 1.0 across all components)
            base_progress = idx / total_components
            component_progress_range = 1.0 / total_components
            
            # Update progress label to show current component
            self.update_progress_text(f"Installing: {description} ({idx + 1}/{total_components})")
            
            self.log(f"Installing {description} ({component})... [{idx + 1}/{total_components}]", "info")
            self.log("  (This may take several minutes - progress will be shown below)", "info")
            
            # Progress callback that updates based on component progress
            def update_component_progress(percent):
                
                # Update progress label to show current component
                self.update_progress_text(f"Installing: {description} ({idx + 1}/{total_components})")
                
                self.log(f"Installing {description} ({component})... [{idx + 1}/{total_components}]", "info")
                self.log("  (This may take several minutes - progress will be shown below)", "info")
                
                # Progress callback that updates based on component progress
                def update_component_progress(percent):
                    # percent is 0.0-1.0 for this component
                    # Map it to overall progress
                    overall_progress = base_progress + (percent * component_progress_range)
                    self.update_progress(overall_progress)
                
                # Check for cancellation before starting installation
                if self.check_cancelled():
                    return
                
                # Use streaming to show progress in real-time
                # Keep --unattended to prevent dialogs, but remove it for verbose output
                # We'll use verbose mode to see progress
                try:
                    success = self.run_command_streaming(
                        ["winetricks", "--unattended", "--verbose", "--force", "--no-isolate", "--optout", component],
                        env=env,
                        progress_callback=update_component_progress
                    )
                    
                    if success and not self.check_cancelled():
                        self.log(f"✓ {description} installed", "success")
                    elif not success and not self.check_cancelled():
                        # If installation failed, try once more with force
                        self.log(f"⚠ {description} installation failed, retrying...", "warning")
                        time.sleep(2)  # Brief pause before retry
                        
                        self.log(f"Retrying {description} installation...", "info")
                        retry_success = self.run_command_streaming(
                            ["winetricks", "--unattended", "--verbose", "--force", "--no-isolate", "--optout", component],
                            env=env,
                            progress_callback=update_component_progress
                        )
                        
                        # Mark component as complete after retry
                        self.update_progress(base_progress + component_progress_range)
                        
                        if retry_success:
                            self.log(f"✓ {description} installed successfully on retry", "success")
                        else:
                            # Check if it might already be installed by checking the component
                            if self._check_winetricks_component(component.split('=')[0] if '=' in component else component, 
                                                                 Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine", env):
                                self.log(f"✓ {description} appears to already be installed", "success")
                            else:
                                self.log(f"✗ {description} installation failed after retry. You may need to install manually.", "error")
                
                except Exception as e:
                    if not self.check_cancelled():
                        self.log(f"Error during Winetricks installation: {e}", "error")
                finally:
                    # Make sure to end the operation even if there was an error or cancellation
                    if hasattr(self, 'current_operation') and self.current_operation == "Installing Winetricks Dependencies":
                        self.end_operation()
                    # Windows 11 compatibility will be set below
        
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
            self.update_progress_text("Ready")
            self.end_operation()
    
    def install_affinity_settings(self):
        """Install Affinity v3 (Unified) settings files to enable settings saving"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Fix Settings (Affinity v3 only)", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log("Note: This fix applies only to Affinity v3 (Unified).", "info")
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please setup Wine environment first.", "error")
            QMessageBox.warning(
                self,
                "Wine Not Ready",
                "Wine setup must complete before installing Affinity v3 settings.\n"
                "Please setup Wine environment first."
            )
            return
        
        # Start operation and wrapper thread
        self.start_operation("Install Affinity v3 Settings")
        threading.Thread(target=self._install_affinity_settings_entry, daemon=True).start()
    
    def _install_affinity_settings_thread(self):
        """Install Affinity v3 (Unified) settings in background thread - downloads repo and copies Settings"""
        # Determine Windows username
        # Wine typically uses "Public" as the default username, but check for existing users
        users_dir = Path(self.directory) / "drive_c" / "users"
        username = "Public"  # Default Wine username
        
        # Check if users directory exists and has other users
        if users_dir.exists():
            # Look for existing user directories (excluding Public, Default, etc.)
            existing_users = [d.name for d in users_dir.iterdir() if d.is_dir() and d.name not in ["Public", "Default", "All Users", "Default User"]]
            if existing_users:
                # Use the first existing user, or fall back to Public
                username = existing_users[0]
                self.log(f"Using existing Windows user: {username}", "info")
            else:
                self.log(f"Using default Windows user: {username}", "info")
        else:
            self.log(f"Creating users directory structure for: {username}", "info")
            users_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temp directory for cloning/downloading
        temp_dir = Path(self.directory) / ".temp_settings"
        if temp_dir.exists():
            self.log("Cleaning up existing temp directory...", "info")
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                self.log(f"Warning: Could not remove existing temp dir: {e}", "warning")
        temp_dir.mkdir(exist_ok=True)
        
        # Download the repository as a zip file
        self.update_progress_text("Downloading Settings from repository...")
        self.update_progress(0.1)
        self.log("Downloading Settings from GitHub repository...", "info")
        repo_zip = temp_dir / "AffinityOnLinux.zip"
        repo_url = "https://github.com/seapear/AffinityOnLinux/archive/refs/heads/main.zip"
        
        if not self.download_file(repo_url, str(repo_zip), "Settings repository"):
            self.log("Failed to download Settings repository", "error")
            self.log(f"  URL: {repo_url}", "error")
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return
        
        # Verify the zip file was downloaded
        if not repo_zip.exists() or repo_zip.stat().st_size == 0:
            self.log("Downloaded zip file is missing or empty", "error")
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return
        
        self.log(f"Downloaded zip file size: {repo_zip.stat().st_size / 1024 / 1024:.2f} MB", "info")
        
        # Extract the zip file
        self.update_progress_text("Extracting Settings repository...")
        self.update_progress(0.3)
        self.log("Extracting Settings repository...", "info")
        try:
            if self.check_command("7z"):
                success, stdout, stderr = self.run_command([
                    "7z", "x", str(repo_zip), f"-o{temp_dir}", "-y"
                ])
                if not success:
                    self.log(f"7z extraction failed: {stderr}", "error")
                    raise Exception("7z extraction failed")
                self.log("Extraction completed with 7z", "success")
            elif self.check_command("unzip"):
                with zipfile.ZipFile(repo_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                self.log("Extraction completed with unzip", "success")
            else:
                self.log("Neither 7z nor unzip available for extraction", "error")
                self.log("Please install 7z or unzip to extract the repository", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            # Find the extracted directory (usually AffinityOnLinux-main)
            extracted_dirs = list(temp_dir.glob("AffinityOnLinux-*"))
            self.log(f"Found {len(extracted_dirs)} extracted director{'y' if len(extracted_dirs) == 1 else 'ies'}", "info")
            
            extracted_dir = extracted_dirs[0] if extracted_dirs else None
            if not extracted_dir:
                self.log("Could not find extracted repository directory", "error")
                self.log(f"Contents of temp_dir: {[d.name for d in temp_dir.iterdir()]}", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            self.log(f"Using extracted directory: {extracted_dir.name}", "info")
            
            # Check if Auxiliary directory exists
            auxiliary_dir = extracted_dir / "Auxiliary"
            if not auxiliary_dir.exists():
                self.log("Auxiliary directory not found in repository", "error")
                self.log(f"Contents of extracted directory: {[d.name for d in extracted_dir.iterdir()]}", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            settings_dir = auxiliary_dir / "Settings"
            if not settings_dir.exists():
                self.log("Settings directory not found in Auxiliary", "error")
                self.log(f"Contents of Auxiliary: {[d.name for d in auxiliary_dir.iterdir()]}", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            # List what's in the Settings directory
            settings_contents = [d.name for d in settings_dir.iterdir() if d.is_dir()]
            self.log(f"Found Settings folders: {settings_contents}", "info")
            
            # Source Settings directory path - For Affinity v3 (Unified), use 3.0
            # $APP would be "Affinity" and version is 3.0
            # So the source should be: Auxiliary/Settings/Affinity/3.0/Settings
            self.update_progress_text("Locating Settings files...")
            self.update_progress(0.5)
            settings_source_dirs = [
                settings_dir / "Affinity" / "3.0" / "Settings",  # Affinity v3 uses 3.0
                settings_dir / "Affinity" / "Settings",
                settings_dir / "Unified" / "3.0" / "Settings",
                settings_dir / "Unified" / "Settings",
            ]
            
            settings_source = None
            for source_dir in settings_source_dirs:
                if source_dir.exists():
                    files = list(source_dir.iterdir())
                    if files:
                        settings_source = source_dir
                        self.log(f"Found settings at: {source_dir.relative_to(extracted_dir)}", "success")
                        self.log(f"  Contains {len(files)} file(s)/folder(s)", "info")
                        break
            
            if not settings_source:
                self.log("Settings directory not found in repository", "error")
                self.log("Tried paths:", "error")
                for path in settings_source_dirs:
                    self.log(f"  - {path.relative_to(extracted_dir)}: {'exists' if path.exists() else 'not found'}", "error")
                
                # List what's actually in Settings/Affinity if it exists
                affinity_settings = settings_dir / "Affinity"
                if affinity_settings.exists():
                    self.log(f"Contents of Settings/Affinity: {[d.name for d in affinity_settings.iterdir()]}", "info")
                
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            # Target directory in Wine prefix
            # Based on Settings.md: mv $APP/3.0/Settings drive_c/users/$USERNAME/AppData/Roaming/Affinity/
            # For Affinity v3, this means: Affinity/3.0/Settings -> AppData/Roaming/Affinity/Affinity/3.0/Settings
            affinity_appdata = users_dir / username / "AppData" / "Roaming" / "Affinity"
            
            # Check what version folder Affinity v3 actually uses by looking at existing structure
            affinity_dir = affinity_appdata / "Affinity"
            version_folder = None
            if affinity_dir.exists():
                existing_versions = [d.name for d in affinity_dir.iterdir() if d.is_dir()]
                if existing_versions:
                    # Prefer 3.0 for Affinity v3
                    if "3.0" in existing_versions:
                        version_folder = "3.0"
                    elif "2.0" in existing_versions:
                        version_folder = "2.0"
                    else:
                        # Use the first one found (sorted)
                        version_folder = sorted(existing_versions)[0]
                    self.log(f"Found existing Affinity version folder: {version_folder}", "info")
            
            # If no existing version folder, use 3.0 for Affinity v3
            if not version_folder:
                # Try to detect from source path
                source_parts = settings_source.parts
                if "3.0" in source_parts:
                    version_folder = "3.0"
                elif "2.0" in source_parts:
                    version_folder = "2.0"
                else:
                    version_folder = "3.0"  # Default to 3.0 for Affinity v3
                self.log(f"Using version folder: {version_folder} (Affinity v3 uses 3.0)", "info")
            
            # Target path: AppData/Roaming/Affinity/Affinity/3.0/Settings (for v3)
            target_dir = affinity_appdata / "Affinity" / version_folder / "Settings"
            
            # Remove existing settings if they exist (to force fresh copy)
            if target_dir.exists():
                self.log(f"Removing existing settings from: {target_dir}", "info")
                try:
                    shutil.rmtree(target_dir)
                    self.log("Old settings removed", "success")
                except Exception as e:
                    self.log(f"Warning: Could not fully remove old settings: {e}", "warning")
            
            # Copy settings from source to target
            self.update_progress_text("Copying Settings files...")
            self.update_progress(0.7)
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            self.log(f"Copying settings from repository to Wine prefix...", "info")
            self.log(f"  From: {settings_source}", "info")
            self.log(f"  To: {target_dir}", "info")
            
            # Copy with metadata preservation
            shutil.copytree(settings_source, target_dir, dirs_exist_ok=True)
            self.update_progress(0.9)
            self.log(f"Settings copied successfully to: {target_dir}", "success")
            
            # Verify the copy
            copied_files = list(target_dir.rglob("*"))
            source_files = list(settings_source.rglob("*"))
            self.log(f"Copied {len(copied_files)} file(s)/folder(s) (source had {len(source_files)})", "success")
            
            # List some of the copied files for verification
            xml_files = list(target_dir.rglob("*.xml"))
            if xml_files:
                self.log(f"Found {len(xml_files)} XML file(s) in settings", "info")
                for xml_file in xml_files[:5]:  # Show first 5
                    self.log(f"  - {xml_file.relative_to(target_dir)}", "info")
            
            # Set permissions (make sure files are readable)
            try:
                import os
                for root, dirs, files in os.walk(target_dir):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o755)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o644)
                self.log("File permissions set correctly", "success")
            except Exception as e:
                self.log(f"Note: Could not set permissions: {e}", "warning")
            
            # Clean up temp files
            try:
                shutil.rmtree(temp_dir)
                self.log("Temp files cleaned up", "info")
            except Exception as e:
                self.log(f"Note: Could not clean up temp files: {e}", "warning")
            
            self.update_progress(1.0)
            self.update_progress_text("Settings installation complete!")
            self.log("\n✓ Affinity v3 settings installation completed!", "success")
            self.log("Settings files have been installed for Affinity v3 (Unified).", "info")
            
        except Exception as e:
            import traceback
            self.log(f"Error installing settings: {e}", "error")
            self.log(f"Traceback: {traceback.format_exc()}", "error")
            # Clean up on error
            try:
                shutil.rmtree(temp_dir)
                repo_zip.unlink(missing_ok=True)
            except:
                pass
    
    def _check_winetricks_component(self, component, wine, env):
        """Check if a winetricks component is installed"""
        try:
            # Different checks for different components
            if component == "dotnet35":
                # Check for .NET 3.5 in registry
                success, stdout, _ = self.run_command(
                    [str(wine), "reg", "query", "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\NET Framework Setup\\NDP\\v3.5", "/v", "Install"],
                    check=False,
                    env=env,
                    capture=True
                )
                if success and stdout:
                    # Check if Install value is 1
                    if "0x1" in stdout or "REG_DWORD" in stdout:
                        return True
            elif component == "dotnet48":
                # Check for .NET 4.8 in registry
                success, stdout, _ = self.run_command(
                    [str(wine), "reg", "query", "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\NET Framework Setup\\NDP\\v4\\Full", "/v", "Release"],
                    check=False,
                    env=env,
                    capture=True
                )
                if success and stdout:
                    # .NET 4.8 has release number 528040 or higher
                    match = re.search(r'0x([0-9a-fA-F]+)', stdout)
                    if match:
                        release = int(match.group(1), 16)
                        if release >= 528040:  # .NET 4.8
                            return True
            elif component == "corefonts":
                # Check if core fonts directory exists
                fonts_dir = Path(self.directory) / "drive_c" / "windows" / "Fonts"
                if fonts_dir.exists():
                    # Check for some common core fonts
                    core_fonts = ["arial.ttf", "times.ttf", "courier.ttf", "tahoma.ttf"]
                    for font in core_fonts:
                        if (fonts_dir / font).exists():
                            return True
            elif component == "vcrun2022":
                # Check for Visual C++ 2022 redistributables
                vcrun_paths = [
                    Path(self.directory) / "drive_c" / "windows" / "system32" / "vcruntime140.dll",
                    Path(self.directory) / "drive_c" / "windows" / "syswow64" / "vcruntime140.dll",
                ]
                for vcrun_path in vcrun_paths:
                    if vcrun_path.exists():
                        return True
            elif component == "msxml3":
                # Check for MSXML3
                msxml3_path = Path(self.directory) / "drive_c" / "windows" / "system32" / "msxml3.dll"
                if msxml3_path.exists():
                    return True
            elif component == "msxml6":
                # Check for MSXML6
                msxml6_path = Path(self.directory) / "drive_c" / "windows" / "system32" / "msxml6.dll"
                if msxml6_path.exists():
                    return True
        except Exception:
            pass
        
        return False
    
    def check_webview2_installed(self):
        """Check if WebView2 Runtime is already installed"""
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine.exists():
            return False
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        # Check for WebView2 installation directory
        webview2_paths = [
            Path(self.directory) / "drive_c" / "Program Files (x86)" / "Microsoft" / "EdgeWebView" / "Application",
            Path(self.directory) / "drive_c" / "Program Files" / "Microsoft" / "EdgeWebView" / "Application",
        ]
        
        for webview2_path in webview2_paths:
            if webview2_path.exists():
                # Check if msedgewebview2.exe exists
                msedgewebview2_exe = webview2_path / "msedgewebview2.exe"
                if msedgewebview2_exe.exists():
                    return True
        
        # Also check registry for WebView2 installation
        try:
            success, stdout, _ = self.run_command(
                [str(wine), "reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"],
                check=False,
                env=env,
                capture=True
            )
            if success:
                return True
        except Exception:
            pass
        
        return False
    
    def install_webview2_runtime(self):
        """Install Microsoft Edge WebView2 Runtime for Affinity v3 (Unified)"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Installing Microsoft Edge WebView2 Runtime (Affinity v3)", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please setup Wine environment first.", "error")
            QMessageBox.warning(
                self,
                "Wine Not Ready",
                "Wine setup must complete before installing WebView2 Runtime.\n"
                "Please setup Wine environment first."
            )
            return
        
        # Start operation and wrapper thread
        self.start_operation("Install WebView2 Runtime")
        threading.Thread(target=self._install_webview2_runtime_entry, daemon=True).start()
    
    def _install_webview2_runtime_entry(self):
        """Wrapper to install WebView2 and end the operation when invoked from the button."""
        try:
            self._install_webview2_runtime_thread()
        finally:
            self.end_operation()

    def _install_webview2_runtime_thread(self):
        """Install Microsoft Edge WebView2 Runtime in background thread"""
        # Check if Wine is set up
        wine_binary = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        if not wine_binary.exists():
            self.log("Wine is not set up yet. Please setup Wine environment first.", "error")
            return False
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        regedit = Path(self.directory) / "ElementalWarriorWine" / "bin" / "regedit"
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        
        # Check if WebView2 Runtime is already installed
        self.log("Checking if WebView2 Runtime is already installed...", "info")
        webview2_installed = False
        
        # Check for WebView2 installation directory
        webview2_paths = [
            Path(self.directory) / "drive_c" / "Program Files (x86)" / "Microsoft" / "EdgeWebView" / "Application",
            Path(self.directory) / "drive_c" / "Program Files" / "Microsoft" / "EdgeWebView" / "Application",
        ]
        
        for webview2_path in webview2_paths:
            if webview2_path.exists():
                # Check if msedgewebview2.exe exists
                msedgewebview2_exe = webview2_path / "msedgewebview2.exe"
                if msedgewebview2_exe.exists():
                    webview2_installed = True
                    self.log(f"WebView2 Runtime found at: {webview2_path}", "success")
                    break
        
        # Also check registry for WebView2 installation
        if not webview2_installed:
            try:
                success, stdout, _ = self.run_command(
                    [str(wine), "reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"],
                    check=False,
                    env=env,
                    capture=True
                )
                if success:
                    webview2_installed = True
                    self.log("WebView2 Runtime found in registry", "success")
            except Exception:
                pass
        
        if webview2_installed:
            self.log("WebView2 Runtime is already installed. Skipping installation.", "info")
            self.log("Verifying configuration...", "info")
            
            # Still configure the compatibility settings even if already installed
            # Step 1: Disable Microsoft Edge Update services (if not already done)
            self.log("Ensuring Edge Update services are disabled...", "info")
            disable_edge_update_reg = Path(self.directory) / "disable-edge-update.reg"
            with open(disable_edge_update_reg, "w") as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                f.write("[HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\edgeupdate]\n")
                f.write("\"Start\"=dword:00000004\n\n")
                f.write("[HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\edgeupdatem]\n")
                f.write("\"Start\"=dword:00000004\n")
            
            self.run_command([str(regedit), str(disable_edge_update_reg)], check=False, env=env)
            disable_edge_update_reg.unlink()
            
            # Step 2: Set msedgewebview2.exe to Windows 7 compatibility (if not already set)
            self.log("Ensuring msedgewebview2.exe Windows 7 compatibility is set...", "info")
            webview2_win7_reg = Path(self.directory) / "webview2-win7-cap.reg"
            with open(webview2_win7_reg, "w") as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                f.write("[HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults]\n\n")
                f.write("[HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults\\msedgewebview2.exe]\n")
                f.write("\"Version\"=\"win7\"\n")
            
            self.run_command([str(regedit), str(webview2_win7_reg)], check=False, env=env)
            webview2_win7_reg.unlink()
            
            self.log("\n✓ WebView2 Runtime configuration verified!", "success")
            self.log("WebView2 Runtime is installed and configured correctly.", "info")
            return True
        
        # WebView2 not found, proceed with installation
        self.log("WebView2 Runtime not found. Proceeding with installation...", "info")
        
        try:
            # Step 1: Set Windows 7 compatibility mode
            self.log("Setting Windows 7 compatibility mode...", "info")
            self.run_command([str(wine_cfg), "-v", "win7"], check=False, env=env)
            self.log("Windows 7 compatibility mode set", "success")
            
            # Step 2: Download Microsoft Edge WebView2 Runtime
            self.log("Downloading Microsoft Edge WebView2 Runtime (v109.0.1518.78)...", "info")
            webview2_url = "https://archive.org/download/microsoft-edge-web-view-2-runtime-installer-v109.0.1518.78/MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
            webview2_file = Path(self.directory) / "MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
            
            if not self.download_file(webview2_url, str(webview2_file), "WebView2 Runtime"):
                self.log("Failed to download WebView2 Runtime", "error")
                return False
            
            self.log("WebView2 Runtime downloaded", "success")
            
            # Step 3: Install WebView2 Runtime
            self.log("Installing Microsoft Edge WebView2 Runtime...", "info")
            self.log("This may take a few minutes...", "info")
            env["WINEDEBUG"] = "-all"
            self.run_command([str(wine), str(webview2_file)], check=False, env=env, capture=False)
            
            # Wait for installation to complete
            time.sleep(5)
            self.log("WebView2 Runtime installation completed", "success")
            
            # Step 4: Disable Microsoft Edge Update services
            self.log("Disabling Microsoft Edge Update services...", "info")
            disable_edge_update_reg = Path(self.directory) / "disable-edge-update.reg"
            with open(disable_edge_update_reg, "w") as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                f.write("[HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\edgeupdate]\n")
                f.write("\"Start\"=dword:00000004\n\n")
                f.write("[HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\edgeupdatem]\n")
                f.write("\"Start\"=dword:00000004\n")
            
            self.run_command([str(regedit), str(disable_edge_update_reg)], check=False, env=env)
            disable_edge_update_reg.unlink()
            self.log("Edge Update services disabled", "success")
            
            # Step 5: Set back to Windows 11 compatibility
            self.log("Setting Windows 11 compatibility mode...", "info")
            self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
            self.log("Windows 11 compatibility mode set", "success")
            
            # Step 6: Set msedgewebview2.exe to Windows 7 compatibility
            self.log("Setting msedgewebview2.exe to Windows 7 compatibility...", "info")
            webview2_win7_reg = Path(self.directory) / "webview2-win7-cap.reg"
            with open(webview2_win7_reg, "w") as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                f.write("[HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults]\n\n")
                f.write("[HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults\\msedgewebview2.exe]\n")
                f.write("\"Version\"=\"win7\"\n")
            
            self.run_command([str(regedit), str(webview2_win7_reg)], check=False, env=env)
            webview2_win7_reg.unlink()
            self.log("msedgewebview2.exe Windows 7 compatibility set", "success")
            
            # Clean up installer file
            if webview2_file.exists():
                webview2_file.unlink()
                self.log("WebView2 installer file removed", "success")
            
            self.log("\n✓ Microsoft Edge WebView2 Runtime installation completed!", "success")
            self.log("WebView2 Runtime v109.0.1518.78 has been installed for Affinity v3.", "info")
            self.log("Help > View Help should now work in Affinity v3.", "info")
            return True
            
        except Exception as e:
            if not self.check_cancelled():
                self.log(f"Error installing WebView2 Runtime: {e}", "error")
            # Try to restore Windows 11 compatibility even if something failed
            try:
                self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
            except:
                pass
            return False
    
    def _install_affinity_settings_entry(self):
        """Wrapper to install Affinity settings and end the operation when invoked from the button."""
        try:
            self._install_affinity_settings_thread()
        finally:
            self.end_operation()

    def _install_affinity_settings_thread(self):
        """Install Affinity v3 (Unified) settings in background thread - downloads repo and copies Settings"""
        try:
            # Determine Windows username
            # Wine typically uses "Public" as the default username, but check for existing users
            users_dir = Path(self.directory) / "drive_c" / "users"
            username = "Public"  # Default Wine username
            
            # Check if users directory exists and has other users
            if users_dir.exists():
                # Look for existing user directories (excluding Public, Default, etc.)
                existing_users = [d.name for d in users_dir.iterdir() if d.is_dir() and d.name not in ["Public", "Default", "All Users", "Default User"]]
                if existing_users:
                    # Use the first existing user, or fall back to Public
                    username = existing_users[0]
                    self.log(f"Using existing Windows user: {username}", "info")
                else:
                    self.log(f"Using default Windows user: {username}", "info")
            else:
                self.log(f"Creating users directory structure for: {username}", "info")
                users_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temp directory for cloning/downloading
            temp_dir = Path(self.directory) / ".temp_settings"
            if temp_dir.exists():
                self.log("Cleaning up existing temp directory...", "info")
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.log(f"Warning: Could not remove existing temp dir: {e}", "warning")
            temp_dir.mkdir(exist_ok=True)
            
            # Download the repository as a zip file
            self.update_progress_text("Downloading Settings from repository...")
            self.update_progress(0.1)
            self.log("Downloading Settings from GitHub repository...", "info")
            repo_zip = temp_dir / "AffinityOnLinux.zip"
            repo_url = "https://github.com/seapear/AffinityOnLinux/archive/refs/heads/main.zip"
            
            if not self.download_file(repo_url, str(repo_zip), "Settings repository"):
                self.log("Failed to download Settings repository", "error")
                self.log(f"  URL: {repo_url}", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            # Verify the zip file was downloaded
            if not repo_zip.exists() or repo_zip.stat().st_size == 0:
                self.log("Downloaded zip file is missing or empty", "error")
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
                return
            
            self.log(f"Downloaded zip file size: {repo_zip.stat().st_size / 1024 / 1024:.2f} MB", "info")
            
            # Extract the zip file
            self.update_progress_text("Extracting Settings repository...")
            self.update_progress(0.3)
            self.log("Extracting Settings repository...", "info")
            try:
                if self.check_command("7z"):
                    success, stdout, stderr = self.run_command([
                        "7z", "x", str(repo_zip), f"-o{temp_dir}", "-y"
                    ])
                    if not success:
                        self.log(f"7z extraction failed: {stderr}", "error")
                        raise Exception("7z extraction failed")
                    self.log("Extraction completed with 7z", "success")
                elif self.check_command("unzip"):
                    with zipfile.ZipFile(repo_zip, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    self.log("Extraction completed with unzip", "success")
                else:
                    self.log("Neither 7z nor unzip available for extraction", "error")
                    self.log("Please install 7z or unzip to extract the repository", "error")
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    return
                
                # Find the extracted directory (usually AffinityOnLinux-main)
                extracted_dirs = list(temp_dir.glob("AffinityOnLinux-*"))
                self.log(f"Found {len(extracted_dirs)} extracted director{'y' if len(extracted_dirs) == 1 else 'ies'}", "info")
                
                extracted_dir = extracted_dirs[0] if extracted_dirs else None
                if not extracted_dir:
                    self.log("Could not find extracted repository directory", "error")
                    self.log(f"Contents of temp_dir: {[d.name for d in temp_dir.iterdir()]}", "error")
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    return
                
                self.log(f"Using extracted directory: {extracted_dir.name}", "info")
                
                # Check if Auxiliary directory exists
                auxiliary_dir = extracted_dir / "Auxiliary"
                if not auxiliary_dir.exists():
                    self.log("Auxiliary directory not found in repository", "error")
                    self.log(f"Contents of extracted directory: {[d.name for d in extracted_dir.iterdir()]}", "error")
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    return
                
                settings_dir = auxiliary_dir / "Settings"
                if not settings_dir.exists():
                    self.log("Settings directory not found in Auxiliary", "error")
                    self.log(f"Contents of Auxiliary: {[d.name for d in auxiliary_dir.iterdir()]}", "error")
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    return
                
                # List what's in the Settings directory
                settings_contents = [d.name for d in settings_dir.iterdir() if d.is_dir()]
                self.log(f"Found Settings folders: {settings_contents}", "info")
                
                # Source Settings directory path - For Affinity v3 (Unified), use 3.0
                # $APP would be "Affinity" and version is 3.0
                # So the source should be: Auxiliary/Settings/Affinity/3.0/Settings
                self.update_progress_text("Locating Settings files...")
                self.update_progress(0.5)
                settings_source_dirs = [
                    settings_dir / "Affinity" / "3.0" / "Settings",  # Affinity v3 uses 3.0
                    settings_dir / "Affinity" / "Settings",
                    settings_dir / "Unified" / "3.0" / "Settings",
                    settings_dir / "Unified" / "Settings",
                ]
                
                settings_source = None
                for source_dir in settings_source_dirs:
                    if source_dir.exists():
                        files = list(source_dir.iterdir())
                        if files:
                            settings_source = source_dir
                            self.log(f"Found settings at: {source_dir.relative_to(extracted_dir)}", "success")
                            self.log(f"  Contains {len(files)} file(s)/folder(s)", "info")
                            break
                
                if not settings_source:
                    self.log("Settings directory not found in repository", "error")
                    self.log("Tried paths:", "error")
                    for path in settings_source_dirs:
                        self.log(f"  - {path.relative_to(extracted_dir)}: {'exists' if path.exists() else 'not found'}", "error")
                    
                    # List what's actually in Settings/Affinity if it exists
                    affinity_settings = settings_dir / "Affinity"
                    if affinity_settings.exists():
                        self.log(f"Contents of Settings/Affinity: {[d.name for d in affinity_settings.iterdir()]}", "info")
                    
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
                    return
                
                # Target directory in Wine prefix
                # Based on Settings.md: mv $APP/3.0/Settings drive_c/users/$USERNAME/AppData/Roaming/Affinity/
                # For Affinity v3, this means: Affinity/3.0/Settings -> AppData/Roaming/Affinity/Affinity/3.0/Settings
                affinity_appdata = users_dir / username / "AppData" / "Roaming" / "Affinity"
                
                # Check what version folder Affinity v3 actually uses by looking at existing structure
                affinity_dir = affinity_appdata / "Affinity"
                version_folder = None
                if affinity_dir.exists():
                    existing_versions = [d.name for d in affinity_dir.iterdir() if d.is_dir()]
                    if existing_versions:
                        # Prefer 3.0 for Affinity v3
                        if "3.0" in existing_versions:
                            version_folder = "3.0"
                        elif "2.0" in existing_versions:
                            version_folder = "2.0"
                        else:
                            # Use the first one found (sorted)
                            version_folder = sorted(existing_versions)[0]
                        self.log(f"Found existing Affinity version folder: {version_folder}", "info")
                
                # If no existing version folder, use 3.0 for Affinity v3
                if not version_folder:
                    # Try to detect from source path
                    source_parts = settings_source.parts
                    if "3.0" in source_parts:
                        version_folder = "3.0"
                    elif "2.0" in source_parts:
                        version_folder = "2.0"
                    else:
                        version_folder = "3.0"  # Default to 3.0 for Affinity v3
                    self.log(f"Using version folder: {version_folder} (Affinity v3 uses 3.0)", "info")
                
                # Target path: AppData/Roaming/Affinity/Affinity/3.0/Settings (for v3)
                target_dir = affinity_appdata / "Affinity" / version_folder / "Settings"
                
                # Remove existing settings if they exist (to force fresh copy)
                if target_dir.exists():
                    self.log(f"Removing existing settings from: {target_dir}", "info")
                    try:
                        shutil.rmtree(target_dir)
                        self.log("Old settings removed", "success")
                    except Exception as e:
                        self.log(f"Warning: Could not fully remove old settings: {e}", "warning")
                
                # Copy settings from source to target
                self.update_progress_text("Copying Settings files...")
                self.update_progress(0.7)
                target_dir.parent.mkdir(parents=True, exist_ok=True)
                self.log(f"Copying settings from repository to Wine prefix...", "info")
                self.log(f"  From: {settings_source}", "info")
                self.log(f"  To: {target_dir}", "info")
                
                # Copy with metadata preservation
                shutil.copytree(settings_source, target_dir, dirs_exist_ok=True)
                self.update_progress(0.9)
                self.log(f"Settings copied successfully to: {target_dir}", "success")
                
                # Verify the copy
                copied_files = list(target_dir.rglob("*"))
                source_files = list(settings_source.rglob("*"))
                self.log(f"Copied {len(copied_files)} file(s)/folder(s) (source had {len(source_files)})", "success")
                
                # List some of the copied files for verification
                xml_files = list(target_dir.rglob("*.xml"))
                if xml_files:
                    self.log(f"Found {len(xml_files)} XML file(s) in settings", "info")
                    for xml_file in xml_files[:5]:  # Show first 5
                        self.log(f"  - {xml_file.relative_to(target_dir)}", "info")
                
                # Set permissions (make sure files are readable)
                try:
                    import os
                    for root, dirs, files in os.walk(target_dir):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), 0o755)
                        for f in files:
                            os.chmod(os.path.join(root, f), 0o644)
                    self.log("File permissions set correctly", "success")
                except Exception as e:
                    self.log(f"Note: Could not set permissions: {e}", "warning")
                
                # Clean up temp files
                try:
                    shutil.rmtree(temp_dir)
                    self.log("Temp files cleaned up", "info")
                except Exception as e:
                    self.log(f"Note: Could not clean up temp files: {e}", "warning")
                
                self.update_progress(1.0)
                self.update_progress_text("Settings installation complete!")
                self.log("\n✓ Affinity v3 settings installation completed!", "success")
                self.log("Settings files have been installed for Affinity v3 (Unified).", "info")
                
            except Exception as e:
                import traceback
                self.log(f"Error installing settings: {e}", "error")
                self.log(f"Traceback: {traceback.format_exc()}", "error")
            try:
                shutil.rmtree(temp_dir)
                repo_zip.unlink(missing_ok=True)
            except Exception:
                pass
        except Exception as e:
            import traceback
            self.log(f"Error installing settings: {e}", "error")
            self.log(f"Traceback: {traceback.format_exc()}", "error")
            # Clean up on error
            try:
                shutil.rmtree(temp_dir)
                repo_zip.unlink(missing_ok=True)
            except:
                pass
    
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
        
        # Detect app name from filename - check multiple patterns
        filename_lower = Path(installer_path).name.lower()
        filename_no_spaces = filename_lower.replace(" ", "").replace("-", "").replace("_", "")
        app_name = None
        
        # Check various patterns that might be in Affinity installer filenames
        if "photo" in filename_lower or "photo" in filename_no_spaces:
            app_name = "Photo"
            self.log(f"Detected: Affinity Photo (from filename: {Path(installer_path).name})", "info")
        elif "designer" in filename_lower or "designer" in filename_no_spaces:
            app_name = "Designer"
            self.log(f"Detected: Affinity Designer (from filename: {Path(installer_path).name})", "info")
        elif "publisher" in filename_lower or "publisher" in filename_no_spaces:
            app_name = "Publisher"
            self.log(f"Detected: Affinity Publisher (from filename: {Path(installer_path).name})", "info")
        else:
            self.log(f"Could not detect Affinity app from filename: {Path(installer_path).name}", "warning")
            self.log("Desktop entry will not be created automatically for non-Affinity apps.", "info")
        
        if app_name:
            self.log(f"Will automatically create desktop entry for {app_name}", "info")
        
        # Start operation and installation
        self.start_operation("Custom Installation")
        threading.Thread(
            target=self._run_custom_installation_entry,
            args=(installer_path, app_name),
            daemon=True
        ).start()
    
    def _run_custom_installation_entry(self, installer_path, app_name):
        """Wrapper: run custom installation and always end operation."""
        try:
            self.run_custom_installation(installer_path, app_name)
        finally:
            self.end_operation()

    def run_custom_installation(self, installer_path, app_name):
        """Run custom installation process"""
        try:
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer with sanitized filename (remove spaces)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
            shutil.copy2(installer_path, installer_file)
            self.log(f"Installer {original_filename} copied to Wine prefix: {installer_file} (WINEPREFIX={self.directory})", "success")
            
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
            
            # Run installer and wait until it finishes, capturing logs (with fallback)
            success = self._run_installer_and_capture(installer_file, env, label="installer")
            if not success and not self.check_cancelled():
                self.log("Installer process exited with a non-zero status", "warning")
            else:
                self.log("Installer succes.")
            # Clean up installer
            # if installer_file.exists():
            #     installer_file.unlink()
            # self.log("Installer file removed", "success")
            
            # Restore WinMetadata
            self.restore_winmetadata()
            
            # If it's an Affinity app, automatically create desktop entry and configure OpenCL
            if app_name in ["Photo", "Designer", "Publisher"]:
                self.log(f"Detected Affinity app: {app_name}, configuring...", "info")
                
                # Wait a bit more to ensure installation is fully complete
                time.sleep(2)
                
                # Configure OpenCL for Affinity apps
                self.configure_opencl(app_name)
                
                # Verify app path exists before creating desktop entry
                app_names = {
                    "Photo": ("Photo", "Photo.exe", "Photo 2"),
                    "Designer": ("Designer", "Designer.exe", "Designer 2"),
                    "Publisher": ("Publisher", "Publisher.exe", "Publisher 2")
                }
                name, exe, dir_name = app_names.get(app_name, ("", "", ""))
                app_path = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / dir_name / exe
                
                if app_path.exists():
                    self.log(f"Found application at: {app_path}", "success")
                    # Automatically create desktop entry
                    # Call directly - create_desktop_entry uses signals so it's thread-safe
                    try:
                        self.create_desktop_entry(app_name)
                        self.log("Desktop entry created successfully", "success")
                    except Exception as e:
                        self.log(f"Error creating desktop entry: {e}", "error")
                else:
                    self.log(f"Warning: Application not found at expected path: {app_path}", "warning")
                    self.log("Desktop entry will not be created automatically.", "warning")
                
                display_name = {
                    "Photo": "Affinity Photo",
                    "Designer": "Affinity Designer",
                    "Publisher": "Affinity Publisher"
                }.get(app_name, app_name)
                
                self.log(f"\n✓ {display_name} installation completed!", "success")
                self.log("You can now launch it from your application menu.", "info")
                
                self.show_message(
                    "Installation Complete",
                    f"{display_name} has been successfully installed!\n\n"
                    "You can launch it from your application menu.",
                    "info"
                )
            else:
                # For non-Affinity apps, just complete without desktop entry
                display_name = app_name if app_name else "Application"
                self.log(f"\n✓ {display_name} installation completed!", "success")
                
                self.show_message(
                    "Installation Complete",
                    f"{display_name} has been successfully installed!\n\n"
                    "You may need to create a desktop entry manually if needed.",
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
        exe_path, ok = QInputDialog.getText(
            self,
            "Executable Path",
            f"Enter the full path to the {app_name} executable:\n\n"
            "Example: C:\\Program Files\\MyApp\\MyApp.exe"
        )
        
        if not ok or not exe_path:
            self.log("Desktop entry creation cancelled.", "warning")
            return
        
        # Ask for icon path (optional)
        icon_path, ok = QInputDialog.getText(
            self,
            "Icon Path (Optional)",
            "Enter the path to an icon file (optional):\n\n"
            "Leave blank to use default icon."
        )
        
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / f"{app_name.replace(' ', '')}.desktop"
        
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        
        # Normalize all paths to strings to avoid double slashes
        wine_str = str(wine)
        directory_str = str(self.directory).rstrip("/")  # Remove trailing slash if present
        
        # Normalize path: convert Windows backslashes to forward slashes, remove double slashes
        exe_path_normalized = exe_path.replace("\\", "/").replace("//", "/")
        # If it's a Windows path starting with C:, convert to Linux path
        if exe_path_normalized.startswith("C:/"):
            exe_path_normalized = directory_str + "/drive_c" + exe_path_normalized[2:]
        
        with open(desktop_file, "w") as f:
            f.write("[Desktop Entry]\n")
            f.write(f"Name={app_name}\n")
            f.write(f"Comment={app_name} installed via Affinity Linux Installer\n")
            if icon_path:
                icon_path_str = str(icon_path).rstrip("/")
                f.write(f"Icon={icon_path_str}\n")
            f.write(f"Path={directory_str}\n")
            # Use Linux path format with proper quoting for spaces
            f.write(f'Exec=env WINEPREFIX={directory_str} {wine_str} "{exe_path_normalized}"\n')
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
        
        # Start operation and update in thread
        self.start_operation(f"Update {display_name}")
        threading.Thread(
            target=self._run_update_entry,
            args=(display_name, installer_path),
            daemon=True
        ).start()
    
    def _run_update_entry(self, display_name, installer_path):
        """Wrapper: run update and always end operation."""
        try:
            self.run_update(display_name, installer_path)
        finally:
            self.end_operation()

    def run_update(self, display_name, installer_path):
        """Run the update process - simple installer without desktop entries or deps"""
        try:
            self.update_progress_text("Preparing update...")
            self.update_progress(0.0)
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer to Wine prefix with sanitized filename (remove spaces)
            self.update_progress_text("Copying installer...")
            self.update_progress(0.2)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
            shutil.copy2(installer_path, installer_file)
            self.log(f"Installer copied to Wine prefix: {installer_file} (WINEPREFIX={self.directory})", "success")
            
            # Set up environment
            self.update_progress_text("Configuring Wine...")
            self.update_progress(0.3)
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            env["WINEDEBUG"] = "-all"
            
            # Run installer with custom Wine
            self.update_progress_text("Running updater...")
            self.update_progress(0.4)
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            self.log("Launching installer...", "info")
            self.log("Follow the installation wizard in the window that opens.", "info")
            self.log("This will update the application without creating desktop entries.", "info")
            
            # Run updater and wait, capturing logs (with fallback)
            success = self._run_installer_and_capture(installer_file, env, label="updater")
            if not success and not self.check_cancelled():
                self.log("Updater process exited with a non-zero status", "warning")
            
            # Clean up installer
            if installer_file.exists():
                installer_file.unlink()
                self.log("Installer file removed", "success")
            
            # Remove Wine desktop entries created by the installer
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            wine_desktop_dir = desktop_dir / "wine" / "Programs"
            
            # Ensure display_name is a string
            if not isinstance(display_name, str):
                display_name = str(display_name) if display_name is not None else ""
            
            # Map display names to possible Wine desktop entry names
            wine_entry_names = []
            if display_name and ("Unified" in display_name or display_name == "Affinity (Unified)"):
                wine_entry_names = ["Affinity.desktop"]
            elif display_name and "Photo" in display_name:
                wine_entry_names = ["Affinity Photo 2.desktop", "Affinity Photo.desktop"]
            elif display_name and "Designer" in display_name:
                wine_entry_names = ["Affinity Designer 2.desktop", "Affinity Designer.desktop"]
            elif display_name and "Publisher" in display_name:
                wine_entry_names = ["Affinity Publisher 2.desktop", "Affinity Publisher.desktop"]
            
            removed_count = 0
            for entry_name in wine_entry_names:
                wine_entry = wine_desktop_dir / entry_name
                if wine_entry.exists():
                    try:
                        wine_entry.unlink()
                        removed_count += 1
                        self.log(f"Removed Wine desktop entry: {entry_name}", "info")
                    except Exception as e:
                        self.log(f"Could not remove {entry_name}: {e}", "error")
            
            # Also check for generic Affinity.desktop if not already checked
            if display_name and "Unified" not in display_name:
                generic_entry = wine_desktop_dir / "Affinity.desktop"
                if generic_entry.exists():
                    try:
                        generic_entry.unlink()
                        self.log("Removed Wine desktop entry: Affinity.desktop", "info")
                    except Exception as e:
                        self.log(f"Could not remove Affinity.desktop: {e}", "error")
            
            if removed_count > 0:
                self.log(f"Cleaned up {removed_count} Wine desktop entr{'y' if removed_count == 1 else 'ies'}", "success")
            
            # Reinstall WinMetadata to avoid corruption
            self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.log("Reinstalling WinMetadata to prevent corruption...", "info")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            
            # Kill Wine processes before removing WinMetadata
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
            
            # Reinstall WinMetadata
            self.log("Installing fresh WinMetadata...", "info")
            self.setup_winmetadata()
            
            # For Affinity v3 (Unified), check and install WebView2 Runtime if needed, then reinstall settings files
            if display_name and ("Unified" in display_name or display_name == "Affinity (Unified)"):
                # Check if WebView2 Runtime is installed, install if missing
                self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log("Checking WebView2 Runtime for Affinity v3...", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                if not self.check_webview2_installed():
                    self.log("WebView2 Runtime not found. Installing automatically...", "info")
                    self._install_webview2_runtime_thread()  # Install synchronously in this thread
                else:
                    self.log("WebView2 Runtime is already installed.", "success")
                
                # Reinstall settings files
                self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log("Reinstalling Affinity v3 settings files...", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                self._install_affinity_settings_thread()
                
                # Patch the DLL to fix settings saving (this is the last step)
                self.update_progress_text("Patching DLL for settings fix...")
                self.update_progress(0.95)
                patch_success = self.patch_affinity_dll(display_name)
                if patch_success:
                    self.log("Settings fix patch applied successfully", "success")
                else:
                    self.log("Settings fix patch was skipped or failed (check log for details)", "warning")
            
            self.update_progress(1.0)
            self.update_progress_text("Update complete!")
            self.log(f"\n✓ {display_name} update completed!", "success")
            self.log("The application has been updated. Use your existing desktop entry to launch it.", "info")
            
            # Refresh installation status to update button states
            QTimer.singleShot(100, self.check_installation_status)
            
            message_text = f"{display_name} has been successfully updated!\n\n"
            message_text += "WinMetadata has been reinstalled to prevent corruption.\n"
            if display_name and ("Unified" in display_name or display_name == "Affinity (Unified)"):
                message_text += "Affinity v3 settings have been reinstalled.\n"
                message_text += "Settings fix patch has been applied (settings should now save properly).\n"
            message_text += "Use your existing desktop entry to launch the application."
            
            self.show_message(
                "Update Complete",
                message_text,
                "info"
            )
        except Exception as e:
            self.log(f"Update error: {e}", "error")
            self.show_message("Update Error", f"An error occurred:\n{e}", "error")
    
    def _run_installation_entry(self, app_name, installer_path):
        """Wrapper: run installation and always end operation."""
        try:
            self.run_installation(app_name, installer_path)
        finally:
            self.end_operation()

    def run_installation(self, app_name, installer_path):
        """Run the installation process"""
        try:
            self.update_progress_text("Preparing installation...")
            self.update_progress(0.0)
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer with sanitized filename (remove spaces)
            self.update_progress_text("Copying installer...")
            self.update_progress(0.1)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
            shutil.copy2(installer_path, installer_file)
            self.log(f"Installer copied to Wine prefix: {installer_file} (WINEPREFIX={self.directory})", "success")
            
            # Set Windows version
            self.update_progress_text("Configuring Wine...")
            self.update_progress(0.2)
            wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
            env = os.environ.copy()
            env["WINEPREFIX"] = self.directory
            self.run_command([str(wine_cfg), "-v", "win11"], check=False, env=env)
            
            # Run installer
            self.update_progress_text("Running installer...")
            self.update_progress(0.3)
            wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
            env["WINEDEBUG"] = "-all"
            self.log("Launching installer...", "info")
            self.log("Follow the installation wizard in the window that opens.", "info")
            self.log("Click 'No' if you encounter any errors.", "warning")
            
            # Run installer and wait, capturing logs (with fallback)
            success = self._run_installer_and_capture(installer_file, env, label="installer")
            if not success and not self.check_cancelled():
                self.log("Installer process exited with a non-zero status", "warning")
            
            # Clean up installer
            self.update_progress(0.5)
            installer_file.unlink()
            self.log("Installer file removed", "success")
            
            # Restore WinMetadata
            self.update_progress_text("Restoring Windows Metadata...")
            self.update_progress(0.6)
            self.restore_winmetadata()
            
            # Configure OpenCL
            self.update_progress_text("Configuring OpenCL...")
            self.update_progress(0.7)
            self.configure_opencl(app_name)
            
            # For Affinity v3 (Unified), check and install WebView2 Runtime if needed
            if app_name == "Add" or app_name == "Affinity (Unified)":
                self.update_progress_text("Checking WebView2 Runtime...")
                self.update_progress(0.8)
                self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log("Checking WebView2 Runtime for Affinity v3...", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                if not self.check_webview2_installed():
                    self.log("WebView2 Runtime not found. Installing automatically...", "info")
                    self._install_webview2_runtime_thread()  # Install synchronously in this thread
                else:
                    self.log("WebView2 Runtime is already installed.", "success")
                
                # Patch the DLL to fix settings saving
                self.update_progress_text("Patching DLL for settings fix...")
                self.update_progress(0.85)
                self.patch_affinity_dll(app_name)
            
            # Create desktop entry
            self.update_progress_text("Creating desktop entry...")
            self.update_progress(0.9)
            self.create_desktop_entry(app_name)
            
            self.update_progress(1.0)
            self.update_progress_text("Installation complete!")
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
    
    def check_dotnet_sdk(self):
        """Check if .NET SDK is installed"""
        # First, try to run dotnet --version
        success, stdout, _ = self.run_command(
            ["dotnet", "--version"],
            check=False,
            capture=True
        )
        if success and stdout:
            version = stdout.strip()
            self.log(f".NET SDK found: {version}", "success")
            return True
        
        # If dotnet command not found, check if it's installed via package manager
        # This is useful when dotnet is installed but not in PATH
        if self.distro in ["fedora", "nobara"]:
            # Check via dnf if package is installed
            success, stdout, _ = self.run_command(
                ["dnf", "list", "installed", "dotnet-sdk-8.0"],
                check=False,
                capture=True
            )
            if success and stdout and "dotnet-sdk-8.0" in stdout:
                self.log(".NET SDK package found via dnf (dotnet-sdk-8.0)", "success")
                # Try to find dotnet in common locations
                common_paths = [
                    "/usr/bin/dotnet",
                    "/usr/local/bin/dotnet",
                    "/opt/dotnet/dotnet",
                    Path.home() / ".dotnet" / "dotnet"
                ]
                for path in common_paths:
                    if Path(path).exists():
                        # Try running it
                        success, stdout, _ = self.run_command(
                            [str(path), "--version"],
                            check=False,
                            capture=True
                        )
                        if success and stdout:
                            version = stdout.strip()
                            self.log(f".NET SDK found at {path}: {version}", "success")
                            return True
                # Package is installed but dotnet command not accessible
                self.log(".NET SDK package is installed but 'dotnet' command not found in PATH", "warning")
                self.log("You may need to add /usr/bin to your PATH or restart your terminal", "info")
                return True  # Return True anyway since package is installed
        
        elif self.distro in ["arch", "cachyos", "endeavouros", "xerolinux"]:
            # Check via pacman for dotnet-sdk-8.0
            success, stdout, _ = self.run_command(
                ["pacman", "-Q", "dotnet-sdk-8.0"],
                check=False,
                capture=True
            )
            if success and stdout and "dotnet-sdk-8.0" in stdout:
                self.log(".NET SDK package found via pacman (dotnet-sdk-8.0)", "success")
                # Try common paths
                common_paths = ["/usr/bin/dotnet", "/usr/local/bin/dotnet"]
                for path in common_paths:
                    if Path(path).exists():
                        success, stdout, _ = self.run_command(
                            [path, "--version"],
                            check=False,
                            capture=True
                        )
                        if success and stdout:
                            version = stdout.strip()
                            self.log(f".NET SDK found at {path}: {version}", "success")
                            return True
                return True  # Package is installed
        
        elif self.distro in ["pikaos", "pop", "debian"]:
            # Check via apt/dpkg
            success, stdout, _ = self.run_command(
                ["dpkg", "-l", "dotnet-sdk-8.0"],
                check=False,
                capture=True
            )
            if success and stdout and "dotnet-sdk-8.0" in stdout:
                self.log(".NET SDK package found via dpkg (dotnet-sdk-8.0)", "success")
                common_paths = ["/usr/bin/dotnet", "/usr/local/bin/dotnet"]
                for path in common_paths:
                    if Path(path).exists():
                        success, stdout, _ = self.run_command(
                            [path, "--version"],
                            check=False,
                            capture=True
                        )
                        if success and stdout:
                            version = stdout.strip()
                            self.log(f".NET SDK found at {path}: {version}", "success")
                            return True
                return True  # Package is installed
        
        return False
    
    def ensure_patcher_files(self, silent=False):
        """Ensure AffinityPatcher files are available in .AffinityLinux/Patch/"""
        try:
            # Source: repo's Patch directory
            script_dir = Path(__file__).parent
            source_patch_dir = script_dir.parent / "Patch"
            
            # Destination: .AffinityLinux/Patch/
            dest_patch_dir = Path(self.directory) / "Patch"
            dest_patch_dir.mkdir(parents=True, exist_ok=True)
            
            # Files to copy
            files_to_copy = ["AffinityPatcher.cs", "AffinityPatcher.csproj"]
            
            files_copied = False
            all_exist = True
            for filename in files_to_copy:
                source_file = source_patch_dir / filename
                dest_file = dest_patch_dir / filename
                
                if source_file.exists():
                    # Only copy if destination doesn't exist or source is newer
                    if not dest_file.exists() or source_file.stat().st_mtime > dest_file.stat().st_mtime:
                        shutil.copy2(source_file, dest_file)
                        files_copied = True
                        if not silent:
                            self.log(f"Copied {filename} to .AffinityLinux/Patch/", "info")
                else:
                    if not silent:
                        self.log(f"Warning: {filename} not found in source Patch directory", "warning")
                    all_exist = False
                
                # Check if destination file exists after copy attempt
                if not dest_file.exists():
                    all_exist = False
            
            if files_copied and not silent:
                self.log("Patcher files are ready in .AffinityLinux/Patch/", "success")
            elif not all_exist and not silent:
                self.log("Some patcher files are missing", "warning")
            
            return all_exist
        except Exception as e:
            if not silent:
                self.log(f"Error ensuring patcher files: {e}", "error")
            return False
    
    def build_affinity_patcher(self):
        """Build the AffinityPatcher .NET project"""
        # Use Patch directory from .AffinityLinux (ensured to be available)
        patch_dir = Path(self.directory) / "Patch"
        
        if not patch_dir.exists():
            self.log(f"Patch directory not found: {patch_dir}", "error")
            return None
        
        csproj_file = patch_dir / "AffinityPatcher.csproj"
        if not csproj_file.exists():
            self.log(f"AffinityPatcher.csproj not found: {csproj_file}", "error")
            return None
        
        self.log(f"Building AffinityPatcher from: {patch_dir}", "info")
        
        # Build the project
        output_dir = patch_dir / "bin" / "Release"
        success, stdout, stderr = self.run_command(
            ["dotnet", "build", str(csproj_file), "-c", "Release", "-o", str(output_dir)],
            check=False,
            capture=True
        )
        
        if not success:
            self.log(f"Failed to build AffinityPatcher: {stderr}", "error")
            if stdout:
                self.log(f"Build output: {stdout}", "warning")
            return None
        
        # Find the built executable - .NET can create different output formats
        # Try common output names
        possible_names = [
            "AffinityPatcher",  # Native executable (Linux)
            "AffinityPatcher.dll",  # DLL (runnable with dotnet)
            "AffinityPatcher.exe",  # Windows executable (unlikely on Linux)
        ]
        
        patcher_exe = None
        for name in possible_names:
            candidate = output_dir / name
            if candidate.exists():
                patcher_exe = candidate
                break
        
        if patcher_exe and patcher_exe.exists():
            self.log(f"AffinityPatcher built successfully: {patcher_exe}", "success")
            return patcher_exe
        else:
            # List what's actually in the output directory for debugging
            if output_dir.exists():
                files = list(output_dir.glob("*"))
                self.log(f"Files in output directory: {[f.name for f in files]}", "warning")
            self.log(f"Built patcher not found at expected location: {output_dir}", "error")
            return None
    
    def run_affinity_patcher(self, dll_path):
        """Run the AffinityPatcher on the specified DLL"""
        if not Path(dll_path).exists():
            self.log(f"DLL not found: {dll_path}", "error")
            return False
        
        # Build the patcher if needed
        patcher_exe = self.build_affinity_patcher()
        if not patcher_exe:
            self.log("Failed to build AffinityPatcher", "error")
            return False
        
        self.log(f"Running AffinityPatcher on: {dll_path}", "info")
        
        # Run the patcher - use dotnet for DLLs, direct execution for native executables
        if patcher_exe.suffix == ".dll":
            cmd = ["dotnet", str(patcher_exe), dll_path]
        else:
            cmd = [str(patcher_exe), dll_path]
        
        success, stdout, stderr = self.run_command(
            cmd,
            check=False,
            capture=True
        )
        
        if success:
            self.log("AffinityPatcher completed successfully", "success")
            if stdout:
                # Log the patcher output
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        if "SUCCESS" in line or "success" in line.lower():
                            self.log(line, "success")
                        elif "ERROR" in line or "error" in line.lower():
                            self.log(line, "error")
                        else:
                            self.log(line, "info")
            return True
        else:
            self.log(f"AffinityPatcher failed: {stderr}", "error")
            if stdout:
                self.log(f"Output: {stdout}", "warning")
            return False
    
    def patch_affinity_dll(self, app_name):
        """Patch the Serif.Affinity.dll for Affinity v3 (Unified)"""
        # Only patch Affinity v3 (Unified)
        if app_name != "Add" and app_name != "Affinity (Unified)":
            return True  # Not applicable, return success
        
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Patching Affinity DLL for settings fix...", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if .NET SDK is available, try to install if missing
        if not self.check_dotnet_sdk():
            self.log(".NET SDK not found. Attempting to install...", "info")
            if not self.install_dotnet_sdk():
                self.log("Failed to install .NET SDK automatically", "warning")
                self.log("Settings patching will be skipped.", "warning")
                self.log("You can install .NET SDK manually:", "info")
                if self.distro in ["arch", "cachyos"]:
                    self.log("  sudo pacman -S dotnet-sdk-8.0", "info")
                elif self.distro in ["endeavouros", "xerolinux"]:
                    self.log("  sudo pacman -S dotnet-sdk-8.0", "info")
                elif self.distro in ["fedora", "nobara"]:
                    self.log("  sudo dnf install dotnet-sdk-8.0", "info")
                elif self.distro in ["pikaos", "pop", "debian"]:
                    self.log("  sudo apt install dotnet-sdk-8.0", "info")
                    self.log("  (May require Microsoft's .NET repository)", "warning")
                elif self.distro in ["opensuse-tumbleweed", "opensuse-leap"]:
                    self.log("  sudo zypper install dotnet-sdk-8.0", "info")
                return False
            else:
                self.log(".NET SDK installed successfully", "success")
        
        # Find the DLL
        dll_path = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / "Affinity" / "Serif.Affinity.dll"
        
        if not dll_path.exists():
            self.log(f"Serif.Affinity.dll not found at: {dll_path}", "warning")
            self.log("The DLL may not be installed yet. Patching will be skipped.", "warning")
            return False
        
        # Run the patcher
        return self.run_affinity_patcher(str(dll_path))
    
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
        
        # Normalize all paths to strings to avoid double slashes
        wine_str = str(wine)
        directory_str = str(self.directory).rstrip("/")  # Remove trailing slash if present
        icon_path_str = str(icon_path)
        app_path_str = str(app_path).replace("\\", "/")  # Ensure forward slashes, no double slashes
        
        with open(desktop_file, "w") as f:
            f.write("[Desktop Entry]\n")
            f.write(f"Name=Affinity {name}\n")
            f.write(f"Comment=A powerful {name.lower()} software.\n")
            f.write(f"Icon={icon_path_str}\n")
            f.write(f"Path={directory_str}\n")
            # Use Linux path format with proper quoting for spaces
            f.write(f'Exec=env WINEPREFIX={directory_str} {wine_str} "{app_path_str}"\n')
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
    
    def _download_affinity_installer_thread(self, save_path_obj: Path):
        """Worker: Download Affinity installer and end operation."""
        download_url = "https://downloads.affinity.studio/Affinity%20x64.exe"
        self.log(f"Downloading from: {download_url}", "info")
        self.log(f"Saving to: {save_path_obj}", "info")
        try:
            if self.download_file(download_url, str(save_path_obj), "Affinity installer"):
                self.log(f"\n✓ Download completed successfully!", "success")
                self.log(f"Installer saved to: {save_path_obj}", "success")
                self.show_message(
                    "Download Complete",
                    "Affinity installer has been downloaded successfully!\n\nYou can now run it with the installer buttons.",
                    "info"
                )
            else:
                self.log("✗ Download failed", "error")
        finally:
            self.end_operation()

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
    
    def open_winetricks(self):
        """Open Winetricks GUI using custom Wine"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Opening Winetricks", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        if not wine_cfg.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        # Check if winetricks is available
        winetricks_path = shutil.which("winetricks")
        if not winetricks_path:
            self.log("Winetricks is not installed. Please install it using your package manager.", "error")
            self.show_message(
                "Winetricks Not Found",
                "Winetricks is not installed. Please install it using:\n\n"
                "Arch/CachyOS/EndeavourOS/XeroLinux: sudo pacman -S winetricks\n"
                "Fedora/Nobara: sudo dnf install winetricks\n"
                "Debian/Ubuntu/Mint/Pop/Zorin/PikaOS: sudo apt install winetricks\n"
                "openSUSE: sudo zypper install winetricks",
                "error"
            )
            return
        
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        
        self.log(f"Opening winetricks using: {winetricks_path}", "info")
        self.log("The Winetricks GUI should open now.", "info")
        
        # Run winetricks in background (non-blocking)
        # Winetricks will open its GUI when run without arguments
        threading.Thread(
            target=lambda: self.run_command([winetricks_path], check=False, capture=False, env=env),
            daemon=True
        ).start()
        
        self.log("✓ Winetricks opened", "success")
    
    def set_windows11_renderer(self):
        """Set Windows 11 and configure renderer (OpenGL or Vulkan)"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Windows 11 + Renderer Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Start operation for renderer configuration
        self.start_operation("Configure Renderer")
        
        wine_cfg = Path(self.directory) / "ElementalWarriorWine" / "bin" / "winecfg"
        
        if not wine_cfg.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.end_operation()
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
            self.end_operation()
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
        self.end_operation()
    
    def install_dotnet_sdk(self):
        """Install .NET SDK based on distribution"""
        try:
            self.log("Installing .NET SDK...", "info")
            
            if self.distro in ["pikaos", "pop", "debian"]:
                # Try installing dotnet-sdk-8.0 (may need Microsoft repo)
                success, _, stderr = self.run_command([
                    "sudo", "apt", "install", "-y", "dotnet-sdk-8.0"
                ], check=False)
                if not success:
                    self.log("Failed to install dotnet-sdk-8.0 from default repos", "warning")
                    self.log("You may need to add Microsoft's .NET repository. See: https://learn.microsoft.com/dotnet/core/install/linux", "info")
                    return False
                return True
            
            commands = {
                "arch": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "dotnet-sdk-8.0"],
                "cachyos": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "dotnet-sdk-8.0"],
                "endeavouros": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "dotnet-sdk-8.0"],
                "xerolinux": ["sudo", "pacman", "-S", "--needed", "--noconfirm", "dotnet-sdk-8.0"],
                "fedora": ["sudo", "dnf", "install", "-y", "dotnet-sdk-8.0"],
                "nobara": ["sudo", "dnf", "install", "-y", "dotnet-sdk-8.0"],
                "opensuse-tumbleweed": ["sudo", "zypper", "install", "-y", "dotnet-sdk-8.0"],
                "opensuse-leap": ["sudo", "zypper", "install", "-y", "dotnet-sdk-8.0"]
            }
            
            if self.distro in commands:
                success, _, stderr = self.run_command(commands[self.distro], check=False)
                if success:
                    self.log(".NET SDK installed successfully", "success")
                    return True
                else:
                    self.log(f"Failed to install .NET SDK: {stderr[:200] if stderr else 'Unknown error'}", "error")
                    return False
            
            self.log(f"Unsupported distribution for .NET SDK auto-install: {self.distro}", "error")
            return False
        except Exception as e:
            self.log(f"Error installing .NET SDK: {e}", "error")
            return False
    
    def fix_affinity_settings(self):
        """Fix Affinity v3 settings by patching the DLL"""
        try:
            self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.log("Fix Affinity v3 Settings", "info")
            self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            
            # Ensure patcher files are available
            self.ensure_patcher_files()
            
            # Check if Affinity v3 is installed
            dll_path = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / "Affinity" / "Serif.Affinity.dll"
            
            if not dll_path.exists():
                self.log("Affinity v3 (Unified) is not installed.", "error")
                self.log(f"Expected DLL at: {dll_path}", "info")
                self.show_message(
                    "Affinity v3 Not Found",
                    "Affinity v3 (Unified) is not installed.\n\n"
                    "This fix only works for Affinity v3 (Unified).\n"
                    "Please install Affinity v3 first using the 'Affinity (Unified)' button.",
                    "error"
                )
                return
            
            self.start_operation("Fix Affinity Settings")
            
            # Check if .NET SDK is installed, if not try to install it
            if not self.check_dotnet_sdk():
                self.log(".NET SDK not found. Attempting to install...", "info")
                try:
                    if not self.install_dotnet_sdk():
                        self.log("Failed to install .NET SDK automatically", "error")
                        self.log("Please install .NET SDK manually:", "info")
                        if self.distro in ["arch", "cachyos"]:
                            self.log("  sudo pacman -S dotnet-sdk-8.0", "info")
                        elif self.distro in ["endeavouros", "xerolinux"]:
                            self.log("  sudo pacman -S dotnet-sdk-8.0", "info")
                        elif self.distro in ["fedora", "nobara"]:
                            self.log("  sudo dnf install dotnet-sdk-8.0", "info")
                        elif self.distro in ["pikaos", "pop", "debian"]:
                            self.log("  sudo apt install dotnet-sdk-8.0", "info")
                            self.log("  (May require Microsoft's .NET repository)", "warning")
                        elif self.distro in ["opensuse-tumbleweed", "opensuse-leap"]:
                            self.log("  sudo zypper install dotnet-sdk-8.0", "info")
                        self.end_operation()
                        self.show_message(
                            ".NET SDK Required",
                            ".NET SDK is required to patch the Affinity DLL.\n\n"
                            "Please install it manually using the commands shown in the log, then try again.",
                            "error"
                        )
                        return
                except Exception as e:
                    self.log(f"Error during .NET SDK installation: {e}", "error")
                    self.end_operation()
                    self.show_message(
                        "Installation Error",
                        f"An error occurred while trying to install .NET SDK:\n{e}\n\n"
                        "Please install .NET SDK manually and try again.",
                        "error"
                    )
                    return
            
            # Patch the DLL
            success = self.patch_affinity_dll("Add")
            
            if success:
                self.log("\n✓ Settings fix completed successfully!", "success")
                self.log("Affinity v3 should now be able to save settings properly.", "info")
                self.log("You may need to restart Affinity for the changes to take effect.", "info")
                self.show_message(
                    "Settings Fix Complete",
                    "The Affinity v3 DLL has been patched successfully!\n\n"
                    "Settings should now save properly.\n"
                    "You may need to restart Affinity for the changes to take effect.",
                    "info"
                )
            else:
                self.log("\n✗ Settings fix failed", "error")
                self.show_message(
                    "Settings Fix Failed",
                    "Failed to patch the Affinity v3 DLL.\n\n"
                    "Please check the log for details.\n"
                    "Make sure .NET SDK is installed if you see related errors.",
                    "error"
                )
        except Exception as e:
            self.log(f"Unexpected error during settings fix: {e}", "error")
            self.show_message(
                "Unexpected Error",
                f"An unexpected error occurred:\n{e}\n\n"
                "Please check the log for details.",
                "error"
            )
        finally:
            self.end_operation()
    
    def set_dpi_scaling(self):
        """Set DPI scaling for Affinity applications"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("DPI Scaling Configuration", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        wine = Path(self.directory) / "ElementalWarriorWine" / "bin" / "wine"
        
        if not wine.exists():
            self.log("Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            self.show_message("Wine Not Found", "Wine is not set up yet. Please run 'Setup Wine Environment' first.", "error")
            return
        
        # Try to get current DPI value from registry
        env = os.environ.copy()
        env["WINEPREFIX"] = self.directory
        current_dpi = 96  # Default value
        
        # Try to read current DPI from registry
        try:
            success, stdout, _ = self.run_command(
                [str(wine), "reg", "query", "HKEY_CURRENT_USER\\Control Panel\\Desktop", "/v", "LogPixels"],
                check=False,
                env=env,
                capture=True
            )
            if success and stdout:
                # Parse the output to extract DPI value
                # Output format: "LogPixels    REG_DWORD    0x000000c0 (192)"
                match = re.search(r'0x[0-9a-fA-F]+|(\d+)', stdout)
                if match:
                    # Try to find hex value first
                    hex_match = re.search(r'0x([0-9a-fA-F]+)', stdout)
                    if hex_match:
                        current_dpi = int(hex_match.group(1), 16)
                    else:
                        # Try decimal
                        dec_match = re.search(r'\((\d+)\)', stdout)
                        if dec_match:
                            current_dpi = int(dec_match.group(1))
        except:
            pass  # Use default if reading fails
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Set DPI Scaling")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(
            "Adjust DPI scaling for Affinity applications.\n"
            "Higher values make UI elements larger.\n\n"
            "Common values:\n"
            "• 96 = 100% (1080p, 24-27 inches)\n"
            "• 120 = 125% (1080p, 13-15 inch laptops)\n"
            "• 144 = 150% (1440p, 27-32 inches)\n"
            "• 192 = 200% (4K, 27-32 inches)"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Current value display
        value_label = QLabel()
        value_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(value_label)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(96)
        slider.setMaximum(480)
        slider.setValue(current_dpi)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(24)  # Show ticks every 24 DPI
        slider.setSingleStep(12)  # Step by 12 DPI for smoother adjustment
        layout.addWidget(slider)
        
        # Min/Max labels
        minmax_layout = QHBoxLayout()
        minmax_layout.addWidget(QLabel("96 (100%)"))
        minmax_layout.addStretch()
        minmax_layout.addWidget(QLabel("480 (500%)"))
        layout.addLayout(minmax_layout)
        
        # Update label when slider changes
        def update_label(value):
            percentage = int((value / 96) * 100)
            value_label.setText(f"DPI: {value} ({percentage}%)")
        
        slider.valueChanged.connect(update_label)
        update_label(current_dpi)  # Set initial value
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Save")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self.log("DPI scaling configuration cancelled", "warning")
            return
        
        selected_dpi = slider.value()
        percentage = int((selected_dpi / 96) * 100)
        
        # Apply DPI setting via registry
        self.log(f"Setting DPI scaling to {selected_dpi} ({percentage}%)...", "info")
        
        # Use wine reg add command
        success, stdout, stderr = self.run_command(
            [
                str(wine), "reg", "add",
                "HKEY_CURRENT_USER\\Control Panel\\Desktop",
                "/v", "LogPixels",
                "/t", "REG_DWORD",
                "/d", str(selected_dpi),
                "/f"
            ],
            check=False,
            env=env
        )
        
        if success:
            self.log(f"✓ DPI scaling set to {selected_dpi} ({percentage}%)", "success")
            self.log("Note: You may need to restart Affinity applications for the change to take effect.", "info")
            self.show_message(
                "DPI Scaling Updated",
                f"DPI scaling has been set to {selected_dpi} ({percentage}%).\n\n"
                "You may need to restart Affinity applications for the change to take effect.",
                "info"
            )
        else:
            self.log(f"✗ Failed to set DPI scaling: {stderr or 'Unknown error'}", "error")
            self.show_message(
                "Error",
                f"Failed to set DPI scaling:\n{stderr or 'Unknown error'}",
                "error"
            )
    
    def uninstall_affinity_linux(self):
        """Uninstall Affinity Linux by deleting the .AffinityLinux folder"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Uninstall Affinity Linux", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Show warning dialog with Yes/No buttons
        reply = QMessageBox.warning(
            self,
            "Uninstall Affinity Linux",
            "WARNING: This will permanently delete the .AffinityLinux folder and all its contents.\n\n"
            "This includes:\n"
            "• All Wine configuration and settings\n"
            "• All installed Affinity applications (Photo, Designer, Publisher, Unified)\n"
            "• All application data and preferences\n"
            "• All downloaded installers and cached files\n"
            "• WebView2 Runtime and other dependencies\n\n"
            "This action CANNOT be undone!\n\n"
            "Do you want to proceed with the uninstall?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log("Uninstall cancelled by user", "warning")
            return
        
        # Stop Wine processes first
        self.log("Stopping Wine processes...", "info")
        try:
            self.run_command(["wineserver", "-k"], check=False)
            time.sleep(2)
            self.log("Wine processes stopped", "success")
        except Exception as e:
            self.log(f"Warning: Could not stop all Wine processes: {e}", "warning")
        
        # Delete the .AffinityLinux folder
        affinity_dir = Path(self.directory)
        if not affinity_dir.exists():
            self.log("Affinity Linux directory not found. Nothing to uninstall.", "warning")
            self.show_message(
                "Nothing to Uninstall",
                "The .AffinityLinux folder does not exist.\n\nNothing to uninstall.",
                "info"
            )
            return
        
        self.log(f"Deleting directory: {affinity_dir}", "info")
        try:
            shutil.rmtree(affinity_dir)
            self.log("✓ .AffinityLinux folder deleted successfully", "success")
            self.log("\n✓ Uninstall completed!", "success")
            self.log("All Affinity Linux files have been removed.", "info")
            
            self.show_message(
                "Uninstall Complete",
                "The .AffinityLinux folder has been successfully deleted.\n\n"
                "All Affinity installations and configurations have been removed.\n\n"
                "You may close this installer now.",
                "info"
            )
            
            # Refresh installation status
            QTimer.singleShot(100, self.check_installation_status)
            
        except PermissionError:
            self.log("✗ Permission denied. Some files may be in use.", "error")
            self.log("Please close all Affinity applications and try again.", "error")
            self.show_message(
                "Uninstall Failed",
                "Permission denied. Some files may be in use.\n\n"
                "Please close all Affinity applications and Wine processes, then try again.",
                "error"
            )
        except Exception as e:
            self.log(f"✗ Failed to delete directory: {e}", "error")
            self.show_message(
                "Uninstall Failed",
                f"Failed to delete the .AffinityLinux folder:\n\n{str(e)}\n\n"
                "You may need to manually delete it.",
                "error"
            )
    
    def launch_affinity_v3(self):
        """Launch Affinity v3 with optimized environment variables"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Launch Affinity v3", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Check if Affinity is installed
        affinity_exe = Path(self.directory) / "drive_c" / "Program Files" / "Affinity" / "Affinity" / "Affinity.exe"
        if not affinity_exe.exists():
            self.log("✗ Affinity v3 is not installed", "error")
            self.log("Please install Affinity v3 first using 'Update Affinity Applications' → 'Affinity (Unified)'", "info")
            self.show_message(
                "Affinity Not Found",
                "Affinity v3 is not installed.\n\nPlease install it first using:\n'Update Affinity Applications' → 'Affinity (Unified)'",
                QMessageBox.Icon.Warning
            )
            return
        
        # Check if Wine is set up
        # Try both possible directory names
        runner_path = Path(self.directory) / "ElementalWarriorWine-x86_64"
        if not runner_path.exists():
            runner_path = Path(self.directory) / "ElementalWarriorWine"
        wine_bin = runner_path / "bin" / "wine"
        if not wine_bin.exists():
            self.log("✗ Wine is not set up", "error")
            self.log("Please run 'Setup Wine Environment' first", "info")
            self.show_message(
                "Wine Not Found",
                "Wine is not set up.\n\nPlease run 'Setup Wine Environment' first.",
                QMessageBox.Icon.Warning
            )
            return
        
        self.log("Setting up environment variables...", "info")
        
        # Prepare environment variables
        env = os.environ.copy()
        
        # Set PATH to include Wine binaries
        runner_path_str = str(runner_path)
        current_path = env.get("PATH", "")
        env["PATH"] = f"{runner_path_str}/bin:{current_path}"
        
        # Set Wine-related environment variables
        env["WINE"] = str(wine_bin)
        env["WINEPREFIX"] = self.directory
        env["WINEDEBUG"] = "-all,fixme-all"
        env["WINEDLLOVERRIDES"] = "opencl="
        
        # DXVK settings
        env["DXVK_ASYNC"] = "0"
        env["DXVK_CONFIG"] = "d3d9.deferSurfaceCreation = True; d3d9.shaderModel = 1"
        env["DXVK_FRAME_RATE"] = "60"
        env["DXVK_LOG_LEVEL"] = "none"
        
        # VKD3D settings
        env["VKD3D_DEBUG"] = "none"
        env["VKD3D_DISABLE_EXTENSIONS"] = "VK_KHR_present_id"
        env["VKD3D_FEATURE_LEVEL"] = "12_1"
        env["VKD3D_FRAME_RATE"] = "60"
        env["VKD3D_SHADER_DEBUG"] = "none"
        env["VKD3D_SHADER_MODEL"] = "6_5"
        
        self.log("✓ Environment variables configured", "success")
        self.log(f"Wine: {wine_bin}", "info")
        self.log(f"WINEPREFIX: {self.directory}", "info")
        self.log(f"Affinity: {affinity_exe}", "info")
        
        # Launch Affinity using wine start
        self.log("\nLaunching Affinity v3...", "info")
        
        # Use wine start to launch the application
        wine_start_cmd = [
            str(wine_bin),
            "start",
            "C:/Program Files/Affinity/Affinity/Affinity.exe"
        ]
        
        try:
            # Launch in background (non-blocking)
            process = subprocess.Popen(
                wine_start_cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            self.log("✓ Affinity v3 launched successfully", "success")
            self.log("The application should open in a moment...", "info")
            
        except Exception as e:
            self.log(f"✗ Failed to launch Affinity v3: {e}", "error")
            self.show_message(
                "Launch Failed",
                f"Failed to launch Affinity v3:\n\n{str(e)}",
                QMessageBox.Icon.Critical
            )
    
    def download_affinity_installer(self):
        """Download the Affinity installer by itself"""
        self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Download Affinity Installer", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Ask user where to save the file
        downloads_dir = Path.home() / "Downloads"
        default_path = downloads_dir / "Affinity-x64.exe"
        
        # Suggest Downloads folder by default, but let user choose
        suggested_path = str(default_path)
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Affinity Installer",
            suggested_path,
            "Executable files (*.exe);;All files (*.*)"
        )
        
        if not save_path:
            self.log("Download cancelled.", "warning")
            return
        
        save_path_obj = Path(save_path)
        
        # Start operation and thread to download
        self.start_operation("Download Affinity Installer")
        threading.Thread(target=self._download_affinity_installer_thread, args=(save_path_obj,), daemon=True).start()
        
        # The rest of the logic should be in the _download_affinity_installer_thread method
        # This is just a placeholder to fix the syntax error
        pass
    
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
