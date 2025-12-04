# System Requirements

## Supported Distributions

### Officially Supported

- Arch Linux
- CachyOS
- EndeavourOS
- Fedora
- Nobara
- openSUSE (Tumbleweed/Leap)
- PikaOS 4 ⚠️ **Note:** Python GUI installer does not work. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- XeroLinux

### Unsupported Distributions (No Support Provided)

The following distributions are **not officially supported** and **no support will be provided** for issues:

- **Linux Mint** - Outdated dependencies. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- **Zorin OS** - Outdated dependencies. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- **Manjaro** - Known stability issues. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- **Ubuntu** - Outdated package management. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- **Pop!_OS** - Outdated package management. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.
- **Debian** - Outdated dependencies. Use [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) instead.

**Important:** While the installer may function on unsupported distributions if dependencies are manually installed, we cannot provide support. The [AppImage](INSTALLATION.md#1-appimage-recommended-for-beginners) is strongly recommended for these distributions.

## Required Dependencies

These are automatically installed by the GUI installer. For legacy scripts, install manually:

- Wine (provided automatically by installer)
- winetricks
- wget, curl
- p7zip or 7z
- tar, jq
- xz (optional)

