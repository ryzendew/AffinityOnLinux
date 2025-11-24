# AffinityOnLinux

A comprehensive solution for running [Affinity software](https://www.affinity.studio/) on GNU/Linux systems using Wine with full OpenCL hardware acceleration support.

<img width="1275" height="1323" alt="image" src="https://github.com/user-attachments/assets/b04e7307-ed95-484d-931a-713aadfe6c47" />


## Warning About Wine 10.17 method

it has major bugs and issues it's why we don't use it.

## Features

- **Hardware Acceleration** - vkd3d-proton and DXVK provide excellent GPU acceleration (recommended). OpenCL support also available with multiple Wine versions (10.4, 10.10, 10.11, 9.14) patched for OpenCL
- **Multiple Wine Versions** - Choose from Wine 10.4 (recommended), 10.4 v2 (older CPUs), 10.10, 10.11, or 9.14 (legacy) - all patched specifically for OpenCL support and GPU compatibility
- **Wine Version Switching** - Easily switch between Wine versions without reinstalling applications
- **Automated Installation** - Streamlined setup process with dependency management
- **Cross-Distribution Support** - Works on modern Linux distributions (PikaOS 4 via AppImage/legacy scripts only - GUI installer not supported, CachyOS, Nobara, Arch, EndeavourOS, XeroLinux, Fedora, openSUSE)
- **Desktop Integration** - Automatic desktop entry and shortcut creation
- **Wine Configuration** - Pre-configured Wine environment optimized for Affinity applications
- **Settings Save now** - Affinity v3 Settings will save.
- **AppImage Release** - Portable standalone AppImage available for easy distribution and use

## AppImage Release

A portable **AppImage** version of the Affinity Linux Installer is now available! The AppImage is a self-contained application that includes everything needed to run the installer without requiring system-wide dependencies.

### What is an AppImage?

An AppImage is a portable application format for Linux that:
- **No Installation Required** - Just download, make executable, and run
- **Self-Contained** - Includes all dependencies bundled within the file
- **Portable** - Can be run from any location (USB drive, Downloads folder, etc.)
- **Distribution Independent** - Works on most modern Linux distributions without modification
- **No Root Access Needed** - Runs without administrator privileges

### Download and Usage

The AppImage is available from the [GitHub Releases page](https://github.com/ryzendew/AffinityOnLinux/releases/tag/10.4-Wine-Affinity).

**Quick Start:**

1. Download the AppImage file from the releases page
2. Make it executable:
   ```bash
   chmod +x AffinityLinuxInstaller-*.AppImage
   ```
3. Run it:
   ```bash
   ./AffinityLinuxInstaller-*.AppImage
   ```

### AppImage Features

The AppImage includes:
- ✅ Full GUI installer functionality
- ✅ Wine 10.4 with patches for AMD GPU fixes (standard installer supports multiple Wine versions: 10.4, 10.4 v2, 10.10, 10.11, 9.14)
- ✅ DXVK support for better graphics performance (NVIDIA, AMD, and Intel GPUs)
- ✅ Automated dependency management
- ✅ All installer features (One-Click Setup, Wine Configuration, etc.)

### Important Notes

- **Graphics Backend**: The AppImage uses DXVK by default for NVIDIA, AMD, and Intel GPUs, providing excellent hardware acceleration. DXVK and vkd3d-proton have largely taken over for OpenCL in modern setups.
- **OpenCL/vkd3d**: The AppImage does **not** include OpenCL/vkd3d support. For OpenCL hardware acceleration, use the Python GUI installer or shell scripts which will download and configure vkd3d-proton separately.
- **Performance**: DXVK and vkd3d-proton offer excellent performance for most use cases and are generally more reliable than OpenCL, especially on AMD GPUs. If you specifically need OpenCL features, use the standard installer methods.
- **CPU Compatibility**: AppImage v2 works on any CPU architecture. Other AppImage versions may have compatibility issues on older CPUs. If you experience issues on an older CPU, try the v2 version.

### When to Use AppImage vs. Standard Installer

**Use the AppImage if:**
- You want a portable, self-contained installer
- You prefer not to install Python/PyQt6 system-wide
- You're testing or trying the installer on a new system
- You need a quick, no-setup solution
- You're using an unsupported distribution (Linux Mint, Zorin OS, Manjaro, Ubuntu, Pop!_OS) - AppImage is strongly recommended
- You have an older CPU - Use AppImage v2 for best compatibility

**Use the Python GUI Installer if:**
- You need full vkd3d-proton/DXVK support (recommended for hardware acceleration)
- You need OpenCL support (NVIDIA works well; AMD and Intel may have issues - see GPU Compatibility Notes)
- You want the latest features and updates
- You prefer running from source
- You're doing a permanent installation

For more information, see the [release notes](https://github.com/ryzendew/AffinityOnLinux/releases/tag/10.4-Wine-Affinity).

## Wine Version

The installer supports multiple Wine versions, all patched specifically for Affinity compatibility:

### Available Wine Versions

- **Wine 10.4 (Recommended)** - Latest version with AMD GPU and OpenCL patches. Best compatibility and performance for most systems.
- **Wine 10.4 v2 (Older CPUs)** - Optimized for older CPUs (V1-V3 generations). Use this if you have a CPU from 2014-2020 (Zen/Broadwell through Zen 2/Coffee Lake).
- **Wine 10.10** - ElementalWarrior Wine 10.10 with AMD GPU and OpenCL patches. Alternative version for testing compatibility.
- **Wine 10.11** - ElementalWarrior Wine 10.11 with AMD GPU and OpenCL patches. Alternative version for testing compatibility.
- **Wine 9.14 (Legacy)** - Legacy version with AMD GPU and OpenCL patches. Fallback option if you encounter issues with newer versions.

### Wine Version Features

All Wine versions are specifically patched for:

- **OpenCL Support** - Full hardware acceleration enabled out of the box
- **AMD GPU Fixes** - Optimized patches for AMD graphics cards
- **Affinity Compatibility** - Additional fixes and optimizations for running Affinity applications

The installer will automatically detect your CPU and recommend the best Wine version for your system. You can switch between Wine versions at any time using the "Switch Wine Version" feature in the GUI installer.

This patched Wine version is automatically downloaded and configured during setup, providing the best experience for Affinity software on Linux.

## Hardware Acceleration

**Note:** vkd3d-proton and DXVK have largely taken over for OpenCL in modern Wine setups, providing better performance and compatibility for GPU acceleration.

### OpenCL Support

OpenCL support is available with all supported Wine versions (10.4, 10.4 v2, 10.10, 10.11, 9.14), all patched for OpenCL, enabling GPU acceleration for improved performance in Affinity applications. The patched Wine versions include specific fixes for OpenCL and AMD GPU compatibility.

### GPU Compatibility Notes

- **NVIDIA GPUs**: OpenCL works well with NVIDIA GPUs. No known issues.
- **AMD GPUs**: OpenCL support on AMD GPUs may have issues. **Important:** I cannot fix AMD OpenCL issues as I do not have access to an AMD GPU for testing and debugging. If you experience OpenCL issues with AMD GPUs, consider using vkd3d-proton or DXVK instead, which provide excellent hardware acceleration and are generally more reliable.
- **Intel GPUs**: OpenCL support on Intel GPUs may have issues. **Important:** I cannot provide support or fix Intel GPU OpenCL issues as I do not have access to an Intel GPU for testing and debugging. If you experience OpenCL issues with Intel GPUs, consider using vkd3d-proton or DXVK instead, which provide excellent hardware acceleration and are generally more reliable.

### vkd3d-proton and DXVK

vkd3d-proton and DXVK are modern alternatives to OpenCL that provide excellent hardware acceleration:
- **vkd3d-proton**: Provides Direct3D 12 support and is automatically configured by the installer
- **DXVK**: Provides Direct3D 11 support and excellent performance for NVIDIA, AMD, and Intel GPUs
- Both are more reliable than OpenCL on many systems and are recommended for better compatibility, especially for AMD and Intel GPUs

<img width="2559" height="1441" alt="OpenCL Hardware Acceleration" src="https://github.com/user-attachments/assets/b5350cbf-09a3-4ba2-9e98-aec86a73986b" />

## Supported Applications

<img src="https://github.com/user-attachments/assets/96ae06f8-470b-451f-ba29-835324b5b552" width="200" alt="Affinity Publisher"/>
<img src="https://github.com/user-attachments/assets/8ea7f748-c455-4ee8-9a94-775de40dbbf3" width="200" alt="Affinity Designer"/>
<img src="https://github.com/user-attachments/assets/c7b70ee5-58e3-46c6-b385-7c3d02749664" width="200" alt="Affinity Photo"/>
<img src="https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-Canva.svg" width="200" alt="Affinity V3"/>

<details>

<summary><strong><span style="color: red;">Python GUI Dependencies Install Me!</span></strong></summary>

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

**PikaOS: Does not work use the Appimage instead**
```bash
sudo apt install python3-pyqt6
```
```
sudo apt install -y python3-pyqt6.qtsvg
```

**Note:** PyQt6 is required to run the GUI installer. The installer will attempt to install it automatically if missing.

**Ubuntu 25.10 Issues:**

If you encounter issues with the GUI on Ubuntu 25.10, install this additional dependency:

```bash
sudo apt install python3-pyqt6.qtsvg
```

</details>

<details>

<summary><strong>GUI Installer Click Me!</strong></summary>

### Python GUI Installer

**Recommended - Modern graphical interface with one-click setup**

A modern PyQt6-based graphical user interface for the Affinity Linux Installer, providing a clean and professional installation experience with a VS Code-inspired dark theme.

**Alternative: AppImage Version**

A portable AppImage version is also available - see the [AppImage Release](#appimage-release) section below for details. The AppImage is self-contained and doesn't require Python/PyQt6 to be installed system-wide.

**Features:**
- **One-Click Full Setup** - Automatically detects your distribution, installs dependencies, sets up Wine (patched for OpenCL and AMD GPU fixes), and configures everything
- **Multiple Wine Versions** - Choose from Wine 10.4 (recommended), 10.4 v2 (older CPUs), 10.10, 10.11, or 9.14 (legacy) - all patched for OpenCL support and AMD GPU fixes
- **Wine Version Switching** - Switch between Wine versions without reinstalling applications or losing your configuration
- **System Setup Tools** - Download Affinity installers and install custom Windows applications using the Wine environment
- **Update Affinity Applications** - Update existing installations without creating new desktop entries or reinstalling dependencies
- **Automatic WebView2 Runtime Installation** - Automatically detects and installs Microsoft Edge WebView2 Runtime for Affinity v3 to enable Help > View Help functionality
- **Automatic Patcher File Management** - Automatically downloads AffinityPatcher files from GitHub if not found locally, ensuring settings fix functionality always works
- **Enhanced Status Detection** - Real-time status display showing:
  - System dependencies (wine, winetricks, wget, curl, etc.)
  - Winetricks dependencies (.NET Framework, Visual C++, MSXML, fonts, Vulkan renderer)
  - WebView2 Runtime installation status
  - Affinity application installation status
  - Current Wine version in use
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
<img width="1280" height="1337" alt="image" src="https://github.com/user-attachments/assets/c05241ff-4dac-4674-a19b-a41a773394fe" />




**Usage:**
1. Run the installer - it will automatically attempt to install PyQt6 if needed
2. Click **"One-Click Full Setup"** for automatic configuration
3. Choose your Wine version (10.4 recommended for most systems, or 10.4 v2 for older CPUs) - Wine will be automatically downloaded and configured with OpenCL and AMD GPU patches
4. Once Wine is set up, use **"Update Affinity Applications"** to install or update Affinity apps
   - For Affinity v3 (Unified), WebView2 Runtime will be automatically installed if missing
5. Use **"Troubleshooting"** tools to:
   - Switch Wine versions if needed (try different versions for better compatibility)
   - Configure Wine settings and renderers
   - Adjust DPI scaling for better UI visibility
   - Reinstall WinMetadata if needed
   - Completely uninstall Affinity Linux if desired
6. Check the status log on startup to see what's installed and what's missing

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
- PikaOS 4 ⚠️ **Note:** The Python GUI installer does not work on PikaOS. Please use the [AppImage version](#appimage-release) instead until this issue is resolved.
- CachyOS
- Nobara
- Arch Linux
- EndeavourOS
- XeroLinux
- Fedora
- openSUSE (Tumbleweed/Leap)

**Unsupported Distributions (No Support Provided):**

The following distributions are not officially supported and **no support will be provided** for issues encountered on these systems:

- **Linux Mint** - Outdated dependencies and package management systems that frequently cause compatibility issues. **Recommended:** Use the [AppImage version](#appimage-release) instead.
- **Zorin OS** - Outdated dependencies and package management systems that frequently cause compatibility issues. **Recommended:** Use the [AppImage version](#appimage-release) instead.
- **Manjaro** - Known for being unstable, buggy, and prone to breakage due to its unique update cycle and package management approach. **Recommended:** Use the [AppImage version](#appimage-release) instead.
- **Ubuntu** - Outdated package management systems. **Recommended:** Use the [AppImage version](#appimage-release) instead.
- **Pop!_OS** - Outdated package management systems. **Recommended:** Use the [AppImage version](#appimage-release) instead.

**Important:** While the installer may still function on these distributions if all required dependencies are manually installed and up-to-date, **we cannot provide support or troubleshooting assistance** for issues encountered on these systems. The reliability and functionality of the installer on these distributions varies greatly and depends heavily on the user's system configuration, dependency versions, and ability to resolve compatibility issues independently.

**For users on unsupported distributions:** The [AppImage version](#appimage-release) is strongly recommended as it is self-contained and avoids dependency conflicts. Note that AppImage v2 works on any CPU, while other AppImage versions may have compatibility issues on older CPUs.

<details>

<summary><strong>System Dependencies</strong></summary>

### Required Dependencies

- Wine (provided automatically - Multiple Wine versions available: 10.4, 10.4 v2, 10.10, 10.11, or 9.14, all patched for OpenCL and AMD GPU fixes)
- winetricks
- wget
- curl
- p7zip or 7z
- tar
- jq
- xz (optional - Python's lzma module can handle .xz archives, but xz command is useful as fallback)

**Note:** These dependencies are automatically installed by the GUI installer during "One-Click Full Setup". For legacy scripts, you may need to install them manually using your distribution's package manager.

### Wine Version

The installer supports multiple Wine versions, all patched specifically for Affinity compatibility:

- **Wine 10.4 (Recommended)** - Latest version with AMD GPU and OpenCL patches. Best compatibility and performance for most systems.
- **Wine 10.4 v2 (Older CPUs)** - Optimized for older CPUs (V1-V3 generations). Use this if you have a CPU from 2014-2020.
- **Wine 10.10** - ElementalWarrior Wine 10.10 with AMD GPU and OpenCL patches. Alternative version for testing compatibility.
- **Wine 10.11** - ElementalWarrior Wine 10.11 with AMD GPU and OpenCL patches. Alternative version for testing compatibility.
- **Wine 9.14 (Legacy)** - Legacy version with AMD GPU and OpenCL patches. Fallback option if you encounter issues with newer versions.

All Wine versions are specifically patched for OpenCL support, AMD GPU fixes, and Affinity compatibility. The installer will automatically detect your CPU and recommend the best Wine version for your system. You can switch between Wine versions at any time using the GUI installer.

This patched Wine version is automatically downloaded and configured during setup, providing the best experience for Affinity software on Linux.

</details>

### PikaOS Special Instructions

**Important:** The Python GUI installer does not work on PikaOS. **Please use the [AppImage version](#appimage-release) instead** until this issue is resolved.

For legacy shell scripts: PikaOS users must replace the built-in Wine with WineHQ staging before installation. The installer scripts will display the required commands automatically.

## Additional Resources

- **[GUI Installer Guide](Guide/GUI-Installer-Guide.md)** - Complete guide for using the Python GUI installer with step-by-step instructions, button explanations, workflows, and troubleshooting
- [Other Software on GNU/Linux](OtherSoftware-on-Linux.md) - Additional software compatibility information
- [Known Issues](Known-issues.md) - Troubleshooting guide for common problems
- [OpenCL Guide](OpenCL-Guide.md) - Detailed OpenCL configuration information

## Contributing

All pull requests are welcome to improve the scripts, documentation, and overall functionality of this project. Contributions help make AffinityOnLinux better for everyone.

## Community

For support, questions, and community discussions, join our Discord server:

[**Join Discord Community**](https://discord.gg/DW2X8MHQuh)

## License

This project provides installation scripts and configurations for running Affinity software on Linux. Affinity software is a commercial product by Serif (Europe) Ltd. Please ensure you have a valid license before installing.

---

**Disclaimer:** This project is not affiliated with, endorsed by, or associated with Serif (Europe) Ltd. All trademarks and registered trademarks are the property of their respective owners.
