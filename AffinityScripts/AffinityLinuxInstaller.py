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
                distro = line.split("=", 1)[1].strip().strip('"').lower()
                # Normalize "pika" to "pikaos" if detected
                if distro == "pika":
                    distro = "pikaos"
                return distro
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
        QButtonGroup, QRadioButton, QInputDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
    from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QShortcut, QKeySequence, QWheelEvent
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
                QButtonGroup, QRadioButton, QInputDialog
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
    print("  openSUSE: sudo zypper install python3-qt6")
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
        self.update_buttons = {}  # Store references to update buttons
        self.log_font_size = 11  # Initial font size for log area
        
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
        
        # Setup zoom functionality
        self.setup_zoom()
        
        # Center window
        self.center_window()
        
        # Don't auto-start initialization - user will click button
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log("Affinity Linux Installer - Ready", "info")
        self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
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
        
        self.log("", "info")  # Empty line for spacing
        
        # Update button states
        for app_name, button in self.update_buttons.items():
            if button is None:
                continue
            
            # Button should be enabled only if Wine is set up AND the app is installed
            is_installed = app_status.get(app_name, False)
            enabled = wine_exists and is_installed
            
            button.setEnabled(enabled)
            if not enabled:
                # Make it visually disabled (grayed out)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #666666;
                        border: 1px solid #3a3a3a;
                        padding: 6px 12px;
                        min-height: 28px;
                        font-size: 11px;
                        font-weight: 500;
                        text-align: left;
                        border-radius: 8px;
                    }
                """)
            else:
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
                border-radius: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #2d2d30;
                color: #cccccc;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
            }
            QFrame {
                background-color: #252526;
                border: none;
                border-radius: 0px;
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
                border-radius: 8px;
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
                border-radius: 8px;
            }
            QProgressBar {
                border: none;
                background-color: #3c3c3c;
                height: 6px;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
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
                color: #cccccc;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #4a4a4a;
                background-color: #3c3c3c;
            }
            QRadioButton::indicator:hover {
                border-color: #5a5a5a;
            }
            QRadioButton::indicator:checked {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            QDialogButtonBox QPushButton {
                border-radius: 8px;
                min-width: 80px;
            }
            QPushButton[zoomButton="true"] {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3a3a3a;
                padding: 4px 8px;
                min-height: 24px;
                max-width: 35px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton[zoomButton="true"]:hover {
                background-color: #3c3c3c;
                border-color: #4a4a4a;
            }
            QPushButton[zoomButton="true"]:disabled {
                background-color: #252526;
                color: #666666;
                border-color: #2d2d2d;
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
        top_bar.setStyleSheet("background-color: #252526; padding: 15px 20px; border-top-left-radius: 0px; border-top-right-radius: 0px;")
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
        
        # Zoom controls
        zoom_container = QWidget()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(5)
        zoom_layout.addStretch()
        
        # Zoom out button
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        self.zoom_out_btn.setProperty("zoomButton", True)
        self.zoom_out_btn.setMaximumWidth(35)
        self.zoom_out_btn.setMinimumWidth(35)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        # Zoom reset button
        self.zoom_reset_btn = QPushButton("🔍")
        self.zoom_reset_btn.setToolTip("Reset Zoom (Ctrl+0)")
        self.zoom_reset_btn.setProperty("zoomButton", True)
        self.zoom_reset_btn.setMaximumWidth(35)
        self.zoom_reset_btn.setMinimumWidth(35)
        self.zoom_reset_btn.clicked.connect(self.zoom_reset)
        zoom_layout.addWidget(self.zoom_reset_btn)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        self.zoom_in_btn.setProperty("zoomButton", True)
        self.zoom_in_btn.setMaximumWidth(35)
        self.zoom_in_btn.setMinimumWidth(35)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        group_layout.addWidget(zoom_container)
        
        # Log output with zoom support
        self.log_text = ZoomableTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", self.log_font_size))
        self.log_text.set_zoom_callbacks(self.zoom_in, self.zoom_out)
        group_layout.addWidget(self.log_text)
        
        # Initialize zoom button states
        self.update_zoom_buttons()
        
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
                ("Download Affinity Installer", self.download_affinity_installer),
                ("Install from File Manager", self.install_from_file),
            ]
        )
        container_layout.addWidget(sys_group)
        
        # Update Affinity Applications section
        app_buttons = [
            ("Affinity (Unified)", "Add"),
            ("Affinity Photo", "Photo"),
            ("Affinity Designer", "Designer"),
            ("Affinity Publisher", "Publisher"),
        ]
        app_group = self.create_button_group(
            "Update Affinity Applications",
            [(text, lambda name=app_name: self.update_application(name)) for text, app_name in app_buttons],
            button_refs=self.update_buttons,
            button_keys=[app_name for _, app_name in app_buttons]
        )
        container_layout.addWidget(app_group)
        
        # Troubleshooting section
        troubleshoot_group = self.create_button_group(
            "Troubleshooting",
            [
                ("Open Wine Configuration", self.open_winecfg),
                ("Open Winetricks", self.open_winetricks),
                ("Set Windows 11 + Renderer", self.set_windows11_renderer),
                ("Fix Settings", self.install_affinity_settings),
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
    
    def create_button_group(self, title, buttons, button_refs=None, button_keys=None):
        """Create a grouped button section"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(2)
        group_layout.setContentsMargins(8, 20, 8, 8)
        
        for idx, button_data in enumerate(buttons):
            # Handle both (text, command) and (text, command, color) formats for backward compatibility
            if len(button_data) == 2:
                text, command = button_data
            else:
                text, command, _ = button_data
            
            btn = QPushButton(text)
            # All buttons now use neutral colors for better readability
            btn.clicked.connect(command)
            group_layout.addWidget(btn)
            
            # Store button reference if requested
            if button_refs is not None and button_keys is not None and idx < len(button_keys):
                button_refs[button_keys[idx]] = btn
        
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
            
            # Normalize "pika" to "pikaos" if detected
            if self.distro == "pika":
                self.distro = "pikaos"
            
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
        
        # Step 4: Install Affinity v3 settings to enable settings saving
        self.update_progress(0.90)
        self.log("Installing Affinity v3 settings files...", "info")
        self._install_affinity_settings_thread()
        
        # Complete!
        self.update_progress(1.0)
        self.log("\n✓ Full setup completed!", "success")
        self.log("You can now install Affinity applications using the buttons above.", "info")
        
        # Refresh installation status to update button states
        QTimer.singleShot(100, self.check_installation_status)
        
        # Ask if user wants to install an Affinity app
        QTimer.singleShot(200, self._prompt_affinity_install)
    
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
                # Download the installer
                self.log(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log(f"Downloading {display_name} Installer", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                
                download_url = "https://downloads.affinity.studio/Affinity%20x64.exe"
                download_dir = Path.home() / ".cache" / "affinity-installer"
                download_dir.mkdir(parents=True, exist_ok=True)
                # Use filename without spaces to avoid issues
                installer_path = download_dir / "Affinity-x64.exe"
                
                self.log(f"Downloading from: {download_url}", "info")
                if self.download_file(download_url, str(installer_path), f"{display_name} installer"):
                    self.log(f"Download completed: {installer_path}", "success")
                else:
                    self.log("Download failed. Please try providing your own installer file.", "error")
                    self.show_message("Download Failed", 
                                     "Failed to download the installer.\n\n"
                                     "You can download it manually from:\n"
                                     "https://downloads.affinity.studio/Affinity%20x64.exe\n\n"
                                     "Then use 'Provide my own installer file' option.",
                                     "error")
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
            
            # Start installation in background thread
            threading.Thread(
                target=self.run_installation,
                args=(app_code, installer_path_str),
                daemon=True
            ).start()
    
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
            "endeavouros": ["sudo", "pacman", "-S", "--needed", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"],
            "xerolinux": ["sudo", "pacman", "-S", "--needed", "wine", "winetricks", "wget", "curl", "p7zip", "tar", "jq", "zstd"],
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
        
        # Refresh installation status to update button states
        QTimer.singleShot(100, self.check_installation_status)
    
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
        
        threading.Thread(target=self._install_affinity_settings_thread, daemon=True).start()
    
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
        self.log("Downloading Settings from GitHub repository...", "info")
        repo_zip = temp_dir / "AffinityOnLinux.zip"
        repo_url = "https://github.com/seapear/AffinityOnLinux/archive/refs/heads/main.zip"
        
        if not self.download_file(repo_url, str(repo_zip), "Settings repository"):
            self.log("Failed to download Settings repository", "error")
            self.log(f"  URL: {repo_url}", "error")
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            return
        
        # Verify the zip file was downloaded
        if not repo_zip.exists() or repo_zip.stat().st_size == 0:
            self.log("Downloaded zip file is missing or empty", "error")
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            return
        
        self.log(f"Downloaded zip file size: {repo_zip.stat().st_size / 1024 / 1024:.2f} MB", "info")
        
        # Extract the zip file
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
                except:
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
                except:
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
                except:
                    pass
                return
            
            settings_dir = auxiliary_dir / "Settings"
            if not settings_dir.exists():
                self.log("Settings directory not found in Auxiliary", "error")
                self.log(f"Contents of Auxiliary: {[d.name for d in auxiliary_dir.iterdir()]}", "error")
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                return
            
            # List what's in the Settings directory
            settings_contents = [d.name for d in settings_dir.iterdir() if d.is_dir()]
            self.log(f"Found Settings folders: {settings_contents}", "info")
            
            # Source Settings directory path - For Affinity v3 (Unified), use 3.0
            # $APP would be "Affinity" and version is 3.0
            # So the source should be: Auxiliary/Settings/Affinity/3.0/Settings
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
                except:
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
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            self.log(f"Copying settings from repository to Wine prefix...", "info")
            self.log(f"  From: {settings_source}", "info")
            self.log(f"  To: {target_dir}", "info")
            
            # Copy with metadata preservation
            shutil.copytree(settings_source, target_dir, dirs_exist_ok=True)
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
            
            self.log("\n✓ Affinity v3 settings installation completed!", "success")
            self.log("Settings files have been installed for Affinity v3 (Unified).", "info")
            self.log(f"Settings location: {target_dir}", "info")
            self.log("", "info")
            self.log("Note: If settings still don't save:", "info")
            self.log("  1. Try launching Affinity v3 once to ensure it creates its directory structure", "info")
            self.log("  2. Check that the Settings folder exists at the path shown above", "info")
            self.log("  3. Verify file permissions allow read/write access", "info")
            
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
            
            # Copy installer with sanitized filename (remove spaces)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
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
            
            # Copy installer to Wine prefix with sanitized filename (remove spaces)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
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
            
            # For Affinity v3 (Unified), reinstall settings files after update
            if display_name and ("Unified" in display_name or display_name == "Affinity (Unified)"):
                self.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.log("Reinstalling Affinity v3 settings files...", "info")
                self.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                self._install_affinity_settings_thread()
            
            self.log(f"\n✓ {display_name} update completed!", "success")
            self.log("The application has been updated. Use your existing desktop entry to launch it.", "info")
            
            # Refresh installation status to update button states
            QTimer.singleShot(100, self.check_installation_status)
            
            message_text = f"{display_name} has been successfully updated!\n\n"
            message_text += "WinMetadata has been reinstalled to prevent corruption.\n"
            if display_name and ("Unified" in display_name or display_name == "Affinity (Unified)"):
                message_text += "Affinity v3 settings have been reinstalled.\n"
            message_text += "Use your existing desktop entry to launch the application."
            
            self.show_message(
                "Update Complete",
                message_text,
                "info"
            )
        except Exception as e:
            self.log(f"Update error: {e}", "error")
            self.show_message("Update Error", f"An error occurred:\n{e}", "error")
    
    def run_installation(self, app_name, installer_path):
        """Run the installation process"""
        try:
            self.log(f"Selected installer: {installer_path}", "success")
            
            # Copy installer with sanitized filename (remove spaces)
            original_filename = Path(installer_path).name
            sanitized_filename = self.sanitize_filename(original_filename)
            installer_file = Path(self.directory) / sanitized_filename
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
        
        # Download the installer
        download_url = "https://downloads.affinity.studio/Affinity%20x64.exe"
        
        self.log(f"Downloading from: {download_url}", "info")
        self.log(f"Saving to: {save_path_obj}", "info")
        
        if self.download_file(download_url, str(save_path_obj), "Affinity installer"):
            self.log(f"\n✓ Download completed successfully!", "success")
            self.log(f"Installer saved to: {save_path_obj}", "success")
            self.show_message(
                "Download Complete",
                f"Affinity installer has been downloaded successfully!\n\n"
                f"Saved to:\n{save_path_obj}\n\n"
                f"You can now use this installer with 'Install from File Manager' or during installation.",
                "info"
            )
        else:
            self.log("Download failed.", "error")
            self.show_message(
                "Download Failed",
                f"Failed to download the Affinity installer.\n\n"
                f"You can try downloading manually from:\n"
                f"https://downloads.affinity.studio/Affinity%20x64.exe",
                "error"
            )
    
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
