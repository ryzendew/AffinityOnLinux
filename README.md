# AffinityOnLinux

A comprehensive solution for running [Affinity software](https://www.affinity.studio/) on GNU/Linux systems using Wine with hardware acceleration support.

<img width="1275" height="1323" alt="Affinity Linux Installer" src="https://github.com/user-attachments/assets/b04e7307-ed95-484d-931a-713aadfe6c47" />

## What is This?

AffinityOnLinux provides an easy way to install and run Affinity Photo, Designer, Publisher, and the unified Affinity v3 application on Linux. The installer automatically sets up Wine (a compatibility layer for running Windows applications) with all necessary configurations, dependencies, and optimizations.

## Quick Start

**New to Linux or want the easiest option?** Use the AppImage:

1. Download the AppImage from [GitHub Releases](https://github.com/ryzendew/AffinityOnLinux/releases/tag/Affinity-wine-10.10-Appimage)
2. Make it executable: `chmod +x Affinity-3-x86_64.AppImage`
3. Run it: `./Affinity-3-x86_64.AppImage`

**Want full features and latest updates?** Use the Python GUI Installer:

```bash
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py | python3
```

## Installation Methods

### 1. AppImage (Recommended for Beginners)

The AppImage is a portable, self-contained installer that works on most Linux distributions without requiring system-wide dependencies.

**Best for:**
- Users on unsupported distributions (Linux Mint, Zorin OS, Manjaro, Ubuntu, Pop!_OS)
- Users who prefer not to install Python/PyQt6 system-wide
- Quick testing or portable installations
- Older CPUs (use AppImage v2 for best compatibility)

**Features:**
- ✅ No installation required - just download and run
- ✅ Self-contained - includes all dependencies
- ✅ DXVK support for excellent graphics performance
- ✅ Full GUI installer functionality

**Limitations:**
- Does not include OpenCL/vkd3d support (use Python GUI installer for this)
- Uses DXVK by default (which is recommended for most users)

**CPU Compatibility:** AppImage v2 works on any CPU. Other versions may have issues on older CPUs.

### 2. Python GUI Installer (Recommended for Full Features)

A modern graphical installer with comprehensive features and automatic dependency management.

**Best for:**
- Users on supported distributions
- Users who need OpenCL/vkd3d support
- Permanent installations
- Users who want the latest features

**Features:**
- One-click full setup with automatic dependency installation
- Multiple Wine versions to choose from
- Wine version switching without reinstalling applications
- Automatic WebView2 Runtime installation for Affinity v3
- DPI scaling configuration
- Comprehensive troubleshooting tools
- Real-time status monitoring

**Installation:**

```bash
# Run directly from GitHub (recommended)
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py | python3

# Or download and run locally
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py -o install.py && python3 install.py
```

**Dependencies:** The installer will attempt to install PyQt6 automatically if missing. For manual installation, see the [Python GUI Dependencies](#python-gui-dependencies) section below.

**Usage:**
1. Run the installer
2. Click **"One-Click Full Setup"** for automatic configuration
3. Choose your Wine version (10.4 recommended for most systems)
4. Use **"Update Affinity Applications"** to install or update Affinity apps
5. Check the status log to see what's installed

📖 **Detailed Guide:** See the [GUI Installer Guide](Guide/GUI-Installer-Guide.md) for step-by-step instructions.

### 3. Legacy Shell Scripts

Command-line installers for users who prefer terminal-based installation.

**Available Scripts:**
- **All-in-One Installer** - Install any Affinity application
- **Individual Installers** - Affinity Photo, Designer, Publisher, or v3 (Unified)
- **Affinity Updater** - Update existing installations

See the [Legacy Scripts](#legacy-scripts) section below for details.

## System Requirements

### Supported Distributions

**Officially Supported:**
- Arch Linux
- CachyOS
- EndeavourOS
- Fedora
- Nobara
- openSUSE (Tumbleweed/Leap)
- PikaOS 4 ⚠️ **Note:** Python GUI installer does not work. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- XeroLinux

**Unsupported Distributions (No Support Provided):**

The following distributions are **not officially supported** and **no support will be provided** for issues:

- **Linux Mint** - Outdated dependencies. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- **Zorin OS** - Outdated dependencies. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- **Manjaro** - Known stability issues. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- **Ubuntu** - Outdated package management. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- **Pop!_OS** - Outdated package management. Use [AppImage](#1-appimage-recommended-for-beginners) instead.
- - **Debian** - Outdated dependencies. Use [AppImage](#1-appimage-recommended-for-beginners) instead.

**Important:** While the installer may function on unsupported distributions if dependencies are manually installed, we cannot provide support. The [AppImage](#1-appimage-recommended-for-beginners) is strongly recommended for these distributions.

### Required Dependencies

These are automatically installed by the GUI installer. For legacy scripts, install manually:

- Wine (provided automatically by installer)
- winetricks
- wget, curl
- p7zip or 7z
- tar, jq
- xz (optional)

## Wine Versions

The installer supports multiple Wine versions, all patched for Affinity compatibility:

| Version | Best For | Description |
|---------|----------|-------------|
| **10.4** (Recommended) | Most users | Latest version with best compatibility and performance |
| **10.4 v2** | Older CPUs | Optimized for CPUs from 2014-2020 (V1-V3 generations) |
| **10.10** | Testing | Alternative version for compatibility testing |
| **10.11** | Testing | Alternative version for compatibility testing |
| **9.14** (Legacy) | Fallback | Legacy version if newer versions have issues |

**All versions include:**
- OpenCL support patches
- AMD GPU compatibility fixes
- Affinity-specific optimizations

The installer automatically detects your CPU and recommends the best version. You can switch between versions anytime using the GUI installer.

## Hardware Acceleration

### vkd3d-proton and DXVK (Recommended)

**vkd3d-proton** and **DXVK** are modern alternatives to OpenCL that provide excellent hardware acceleration:

- **vkd3d-proton**: Direct3D 12 support (automatically configured)
- **DXVK**: Direct3D 11 support with excellent performance
- **More reliable** than OpenCL on many systems
- **Recommended** for better compatibility, especially on AMD and Intel GPUs

These are automatically configured by the installer and are the recommended method for hardware acceleration.

### OpenCL Support

OpenCL support is available with all Wine versions but may have compatibility issues depending on your GPU.

**GPU Compatibility:**

- **NVIDIA GPUs**: ✅ OpenCL works well. No known issues. Wine GPU bugs can typically be addressed.
- **AMD GPUs**: ⚠️ OpenCL may have issues. **Important:** I cannot fix AMD OpenCL issues or Wine GPU bugs as I do not have access to an AMD GPU for testing. Use vkd3d-proton or DXVK instead (recommended).
- **Intel GPUs**: ⚠️ OpenCL may have issues. **Important:** I cannot fix Intel GPU OpenCL issues or Wine GPU bugs as I do not have access to an Intel GPU for testing. Use vkd3d-proton or DXVK instead (recommended).

**Recommendation:** For AMD and Intel GPUs, use vkd3d-proton or DXVK instead of OpenCL for better reliability and performance.

## Supported Applications

The installer supports all Affinity applications:

- **Affinity Photo** - Professional photo editing
- **Affinity Designer** - Vector graphic design
- **Affinity Publisher** - Desktop publishing
- **Affinity v3 (Unified)** - All-in-one application combining Photo, Designer, and Publisher

## Python GUI Dependencies

If the installer cannot automatically install PyQt6, install it manually:

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

**PikaOS:** Does not work with GUI installer. Use [AppImage](#1-appimage-recommended-for-beginners) instead.

**Ubuntu 25.10:** If you encounter GUI issues, also install:
```bash
sudo apt install python3-pyqt6.qtsvg
```

## Legacy Scripts

<details>
<summary><strong>Click to expand legacy script options</strong></summary>

### All-in-One Installer

Install any Affinity application with automatic dependency management:

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.sh)"
```

### Individual Application Installers

**Affinity Photo:**
```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityPhoto.sh)"
```

**Affinity Designer:**
```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityDesigner.sh)"
```

**Affinity Publisher:**
```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityPublisher.sh)"
```

**Affinity v3 (Unified):**
```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/Affinityv3.sh)"
```

### Affinity Updater

Update existing installations without full reinstallation:

```bash
bash -c "$(curl -s https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityUpdater.sh)"
```

</details>

## Additional Resources

- **[GUI Installer Guide](Guide/GUI-Installer-Guide.md)** - Complete step-by-step guide with troubleshooting
- **[Known Issues](Known-issues.md)** - Common problems and solutions
- **[OpenCL Guide](OpenCL-Guide.md)** - Detailed OpenCL configuration
- **[Other Software on Linux](OtherSoftware-on-Linux.md)** - Additional compatibility information

## Getting Help

- **Discord Community:** [Join our Discord server](https://discord.gg/DW2X8MHQuh) for support and discussions
- **GitHub Issues:** Report bugs and request features on GitHub
- **Documentation:** Check the guides and documentation linked above

## Important Notes

### Wine 10.17 Warning

Wine 10.17 has major bugs and issues. This installer does not use it.

### Support Limitations

- **AMD/Intel GPU Issues:** I cannot fix OpenCL or Wine GPU bugs for AMD/Intel GPUs as I do not have access to these GPUs for testing. Use vkd3d-proton or DXVK instead.
- **Unsupported Distributions:** No support provided for Linux Mint, Zorin OS, Manjaro, Ubuntu, or Pop!_OS. Use AppImage at your own risk.
- **PikaOS:** GUI installer does not work. Use AppImage instead.

## Contributing

Contributions are welcome! Pull requests help improve the project for everyone. Please ensure your changes are tested and documented.

## License

This project provides installation scripts and configurations for running Affinity software on Linux. Affinity software is a commercial product by Serif (Europe) Ltd. Please ensure you have a valid license before installing.

---

**Disclaimer:** This project is not affiliated with, endorsed by, or associated with Serif (Europe) Ltd. All trademarks and registered trademarks are the property of their respective owners.
