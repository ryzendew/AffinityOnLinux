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

<details>
<summary><strong>Python GUI Dependencies</strong></summary>

The installer will attempt to install PyQt6 automatically if missing. If automatic installation fails, install it manually:

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

**PikaOS:** Does not work with GUI installer. Use AppImage instead.

**Ubuntu 25.10:** If you encounter GUI issues, also install:
```bash
sudo apt install python3-pyqt6.qtsvg
```

</details>

## Documentation

### Getting Started
- **[Installation Guide](docs/INSTALLATION.md)** - Complete installation instructions for all methods
- **[System Requirements](docs/SYSTEM-REQUIREMENTS.md)** - Supported distributions and dependencies
- **[GUI Installer Guide](Guide/GUI-Installer-Guide.md)** - Step-by-step GUI installer instructions

### Technical Details
- **[Wine Versions](docs/WINE-VERSIONS.md)** - Available Wine versions and recommendations
- **[Hardware Acceleration](docs/HARDWARE-ACCELERATION.md)** - GPU acceleration options (vkd3d-proton, DXVK, OpenCL)
- **[OpenCL Guide](docs/OpenCL-Guide.md)** - Detailed OpenCL configuration
- **[Legacy Scripts](docs/LEGACY-SCRIPTS.md)** - Command-line installation scripts

### Additional Resources
- **[Known Issues](docs/Known-issues.md)** - Common problems and solutions
- **[Other Software on Linux](docs/OtherSoftware-on-Linux.md)** - Additional compatibility information
- **[Settings Guide](Guide/Settings.md)** - Configuration options

## Getting Help

- **Discord Community:** [Join our Discord server](https://discord.gg/DW2X8MHQuh) for support and discussions
- **GitHub Issues:** Report bugs and request features on GitHub
- **Documentation:** Check the guides and documentation linked above

## Important Notes

### Support Limitations

- **AMD/Intel GPU Issues:** I cannot fix OpenCL or Wine GPU bugs for AMD/Intel GPUs as I do not have access to these GPUs for testing. Use vkd3d-proton or DXVK instead (see [Hardware Acceleration](docs/HARDWARE-ACCELERATION.md)).
- **Unsupported Distributions:** No support provided for Linux Mint, Zorin OS, Manjaro, Ubuntu, or Pop!_OS. Use AppImage at your own risk (see [System Requirements](docs/SYSTEM-REQUIREMENTS.md)).
- **PikaOS:** GUI installer does not work. Use AppImage instead.

### Wine 10.17 Warning

Wine 10.17 has major bugs and issues. This installer does not use it.

## Contributing

Contributions are welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project provides installation scripts and configurations for running Affinity software on Linux. Affinity software is a commercial product by Serif (Europe) Ltd. Please ensure you have a valid license before installing.

---

**Disclaimer:** This project is not affiliated with, endorsed by, or associated with Serif (Europe) Ltd. All trademarks and registered trademarks are the property of their respective owners.
