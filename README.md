# AffinityOnLinux

A comprehensive solution for running [Affinity software](https://www.affinity.studio/) on GNU/Linux systems using Wine with full OpenCL hardware acceleration support.

## Features

- **Full OpenCL Support** - Hardware acceleration enabled out of the box
- **Automated Installation** - Streamlined setup process with dependency management
- **Cross-Distribution Support** - Works on modern Linux distributions (PikaOS 4, CachyOS, Nobara, Arch, EndeavourOS, XeroLinux, Fedora, openSUSE)
- **Desktop Integration** - Automatic desktop entry and shortcut creation
- **Wine Configuration** - Pre-configured Wine environment optimized for Affinity applications

## OpenCL Hardware Acceleration

OpenCL support is fully functional, enabling GPU acceleration for improved performance in Affinity applications.

<img width="2559" height="1441" alt="OpenCL Hardware Acceleration" src="https://github.com/user-attachments/assets/b5350cbf-09a3-4ba2-9e98-aec86a73986b" />

## Supported Applications

<img src="https://github.com/user-attachments/assets/96ae06f8-470b-451f-ba29-835324b5b552" width="200" alt="Affinity Publisher"/>
<img src="https://github.com/user-attachments/assets/8ea7f748-c455-4ee8-9a94-775de40dbbf3" width="200" alt="Affinity Designer"/>
<img src="https://github.com/user-attachments/assets/c7b70ee5-58e3-46c6-b385-7c3d02749664" width="200" alt="Affinity Photo"/>
<img src="https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-Canva.svg" width="200" alt="Affinity V3"/>

<details>

<summary><strong>Python GUI Framework Requirements</strong></summary>

**Arch/CachyOS/EndeavourOS/XeroLinux:**
```bash
sudo pacman -S python-pyqt6
```

**Fedora/Nobara:**
```bash
sudo dnf install python3-pyqt6
```

**openSUSE (Tumbleweed/Leap):**
```bash
sudo zypper install python313-PyQt6
```

**PikaOS:**
```bash
sudo apt install python3-pyqt6
```

**Note:** PyQt6 is required to run the GUI installer. The installer will attempt to install it automatically if missing.

**Ubuntu 25.10 Issues:**

If you encounter issues with the GUI on Ubuntu 25.10, install this additional dependency:

```bash
sudo apt install python3-pyqt6.qtsvg
```

</details>

<details>

<summary><strong>Installation</strong></summary>

### Python GUI Installer

**Recommended - Modern graphical interface with one-click setup**

A modern PyQt6-based graphical user interface for the Affinity Linux Installer, providing a clean and professional installation experience with a VS Code-inspired dark theme.

**Features:**
- **One-Click Full Setup** - Automatically detects your distribution, installs dependencies, sets up Wine, and configures everything
- **System Setup Tools** - Download Affinity installers and install custom Windows applications using the Wine environment
- **Update Affinity Applications** - Update existing installations without creating new desktop entries or reinstalling dependencies
- **Automatic WebView2 Runtime Installation** - Automatically detects and installs Microsoft Edge WebView2 Runtime for Affinity v3 to enable Help > View Help functionality
- **Enhanced Status Detection** - Real-time status display showing:
  - System dependencies (wine, winetricks, wget, curl, etc.)
  - Winetricks dependencies (.NET Framework, Visual C++, MSXML, fonts, Vulkan renderer)
  - WebView2 Runtime installation status
  - Affinity application installation status
- **DPI Scaling Configuration** - Adjust DPI scaling for Affinity applications with an intuitive slider (96-480 DPI range) to optimize UI size for different displays
- **Troubleshooting Tools**:
  - Open Wine Configuration (winecfg)
  - Open Winetricks GUI
  - Set Windows 11 + Renderer (Vulkan/OpenGL/GDI)
  - Reinstall WinMetadata (fixes corrupted Windows metadata)
  - Install WebView2 Runtime manually (for Affinity v3)
  - Set DPI Scaling
  - **Uninstall** - Completely remove the .AffinityLinux folder and all installations
- **Custom Installation** - Install any Windows application using the custom Wine environment
- **Visual Progress Tracking** - Real-time progress bars and detailed logging
- **Modern UI** - Clean, organized interface with grouped button sections and rounded corners
- **Zoom Controls** - Adjustable log output font size with zoom buttons (🔍➖, 🔍, 🔍➕) or keyboard shortcuts (Ctrl++/Ctrl+-/Ctrl+0)

**Installation:**

Run directly from GitHub (recommended):
```bash
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py | python3
```

Or download and run locally:
```bash
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py -o install.py && python3 install.py
```

Or clone the repository and run locally:
```bash
python AffinityScripts/AffinityLinuxInstaller.py
```
<img width="1280" height="1440" alt="image" src="https://github.com/user-attachments/assets/44ba7b58-204f-4fa8-9fb8-2cdea9f32c50" />



**Usage:**
1. Run the installer - it will automatically attempt to install PyQt6 if needed
2. Click **"One-Click Full Setup"** for automatic configuration
3. Once Wine is set up, use **"Update Affinity Applications"** to install or update Affinity apps
   - For Affinity v3 (Unified), WebView2 Runtime will be automatically installed if missing
4. Use **"Troubleshooting"** tools to:
   - Configure Wine settings and renderers
   - Adjust DPI scaling for better UI visibility
   - Reinstall WinMetadata if needed
   - Completely uninstall Affinity Linux if desired
5. Check the status log on startup to see what's installed and what's missing

**📖 Need Help?** Check out the [GUI Installer Guide](Guide/GUI-Installer-Guide.md) for detailed step-by-step instructions, button explanations, and troubleshooting tips.

**Zoom Controls:**
- **Zoom In**: Click the **🔍➕** button or press `Ctrl++` / `Ctrl+=`
- **Zoom Out**: Click the **🔍➖** button or press `Ctrl+-` / `Ctrl+Minus`
- **Reset Zoom**: Click the **🔍** button or press `Ctrl+0`
- **Mouse Wheel Zoom**: Hold `Ctrl` and scroll with the mouse wheel over the log area
- Font size range: 6px (minimum) to 48px (maximum), default: 11px

<details>

<summary><strong><big>Legacy Scripts</big></strong></summary>

### All-in-One Installer

The unified installer provides a single interface to install any Affinity application with automatic dependency management and an interactive menu.

**Features:**
- Automatic Linux distribution detection
- Dependency installation and verification
- Interactive application selection menu
- Drag-and-drop installer file support
- Automatic desktop entry creation

**Installation:**

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.sh)"
```

### Individual Application Installers

For users who prefer to install applications individually, dedicated installers are available:

#### <img src="https://github.com/user-attachments/assets/c7b70ee5-58e3-46c6-b385-7c3d02749664" alt="Affinity Photo" width="40"/> **Affinity Photo**

Professional photo editing and image manipulation software with advanced tools for photographers and digital artists. Features include RAW editing, HDR merge, focus stacking, and comprehensive retouching capabilities.

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityPhoto.sh)"
```

#### <img src="https://github.com/user-attachments/assets/8ea7f748-c455-4ee8-9a94-775de40dbbf3" alt="Affinity Designer" width="40"/> **Affinity Designer**

Vector graphic design software for creating illustrations, logos, UI designs, print projects, and mock-ups. Combines vector and raster workflows in a single application with precision drawing tools and professional typography support.

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityDesigner.sh)"
```

#### <img src="https://github.com/user-attachments/assets/96ae06f8-470b-451f-ba29-835324b5b552" alt="Affinity Publisher" width="40"/> **Affinity Publisher**

Desktop publishing application for creating professional layouts, magazines, books, and print materials. Features advanced text handling, master pages, tables, and seamless integration with other Affinity applications.

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityPublisher.sh)"
```

#### <img src="https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-V3.svg" alt="Affinity V3" width="40"/> **Affinity V3 Suite (Unified Application)**

The new unified Affinity application that combines Photo, Designer, and Publisher into a single modern interface. Access all creative tools from one application with seamless workflow integration and a streamlined user experience.

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/Affinityv3.sh)"
```

### Affinity Updater

The Affinity Updater provides a lightweight way to update your existing Affinity installations without going through the full installation process.

**Features:**
- Updates only the application binary
- Preserves existing desktop entries and configurations
- No dependency checks or Wine reconfiguration
- Simple drag-and-drop interface

**Usage:**

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityUpdater.sh)"
```

</details>

</details>

## System Requirements

### Supported Distributions

**Officially Supported:**
- PikaOS 4
- CachyOS
- Nobara
- Arch Linux
- EndeavourOS
- XeroLinux
- Fedora
- openSUSE (Tumbleweed/Leap)

**Note:** Ubuntu, Linux Mint, Pop!_OS, and Zorin OS are not officially supported due to outdated package management systems. Users on these distributions must manually install dependencies.

<details>

<summary><strong>System Dependencies</strong></summary>

### Required Dependencies

- Wine (ElementalWarriorWine provided automatically)
- winetricks
- wget
- curl
- p7zip or 7z
- tar
- jq
- zstd

**Note:** These dependencies are automatically installed by the GUI installer during "One-Click Full Setup". For legacy scripts, you may need to install them manually using your distribution's package manager.

</details>

### PikaOS Special Instructions

PikaOS users must replace the built-in Wine with WineHQ staging before installation. The installer scripts will display the required commands automatically.

## Additional Resources

- **[GUI Installer Guide](Guide/GUI-Installer-Guide.md)** - Complete guide for using the Python GUI installer with step-by-step instructions, button explanations, workflows, and troubleshooting
- [Other Software on GNU/Linux](https://github.com/Twig6943/AffinityOnLinux/blob/main/OtherSoftware-on-Linux.md) - Additional software compatibility information
- [Known Issues](https://github.com/Twig6943/AffinityOnLinux/blob/main/Known-issues.md) - Troubleshooting guide for common problems
- [OpenCL Guide](https://github.com/Twig6943/AffinityOnLinux/blob/main/OpenCL-Guide.md) - Detailed OpenCL configuration information

## Contributing

All pull requests are welcome to improve the scripts, documentation, and overall functionality of this project. Contributions help make AffinityOnLinux better for everyone.

## Community

For support, questions, and community discussions, join our Discord server:

[**Join Discord Community**](https://discord.gg/DW2X8MHQuh)

## License

This project provides installation scripts and configurations for running Affinity software on Linux. Affinity software is a commercial product by Serif (Europe) Ltd. Please ensure you have a valid license before installing.

---

**Disclaimer:** This project is not affiliated with, endorsed by, or associated with Serif (Europe) Ltd. All trademarks and registered trademarks are the property of their respective owners.
