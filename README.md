# AffinityOnLinux

A comprehensive solution for running [Affinity software](https://www.affinity.studio/) on GNU/Linux systems using Wine with full OpenCL hardware acceleration support.

## Features

- **Full OpenCL Support** - Hardware acceleration enabled out of the box
- **Automated Installation** - Streamlined setup process with dependency management
- **Cross-Distribution Support** - Works on modern Linux distributions (PikaOS 4, CachyOS, Nobara, Arch, Fedora, openSUSE)
- **Desktop Integration** - Automatic desktop entry and shortcut creation
- **Wine Configuration** - Pre-configured Wine environment optimized for Affinity applications

## OpenCL Hardware Acceleration

OpenCL support is fully functional, enabling GPU acceleration for improved performance in Affinity applications.

<img width="2559" height="1441" alt="OpenCL Hardware Acceleration" src="https://github.com/user-attachments/assets/b5350cbf-09a3-4ba2-9e98-aec86a73986b" />

## Supported Applications

<img src="https://github.com/user-attachments/assets/96ae06f8-470b-451f-ba29-835324b5b552" width="200" alt="Affinity Publisher"/>
<img src="https://github.com/user-attachments/assets/8ea7f748-c455-4ee8-9a94-775de40dbbf3" width="200" alt="Affinity Designer"/>
<img src="https://github.com/user-attachments/assets/c7b70ee5-58e3-46c6-b385-7c3d02749664" width="200" alt="Affinity Photo"/>
<img src="https://github.com/seapear/AffinityOnLinux/raw/main/Assets/Icons/Affinity-V3.svg" width="200" alt="Affinity V3"/>

## Installation

### All-in-One Installer (Recommended)

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

## Updating Existing Installations

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

## System Requirements

### Supported Distributions

**Officially Supported:**
- PikaOS 4
- CachyOS
- Nobara
- Arch Linux
- Fedora
- openSUSE (Tumbleweed/Leap)

**Note:** Ubuntu, Linux Mint, Pop!_OS, and Zorin OS are not officially supported due to outdated package management systems. Users on these distributions must manually install dependencies.

### Required Dependencies

- Wine (ElementalWarriorWine provided automatically)
- winetricks
- wget
- curl
- p7zip or 7z
- tar
- jq
- zstd

### PikaOS Special Instructions

PikaOS users must replace the built-in Wine with WineHQ staging before installation. The installer scripts will display the required commands automatically.

## Additional Resources

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
