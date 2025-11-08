# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AffinityOnLinux enables running Affinity software (Photo, Designer, Publisher, and V3 Suite) on GNU/Linux using Wine with OpenCL hardware acceleration. The project provides both a modern PyQt6 GUI installer and legacy shell scripts for automated setup and configuration.

## Architecture

### Core Installation Approach

The project uses a custom Wine build (`ElementalWarriorWine`) with OpenCL support through vkd3d-proton. All installations are isolated in `~/.AffinityLinux`:

```
~/.AffinityLinux/
├── ElementalWarriorWine/          # Custom Wine build
├── drive_c/                       # Wine prefix (Windows filesystem)
│   ├── Program Files/Affinity/
│   │   ├── Photo 2/              # Affinity Photo
│   │   ├── Designer 2/           # Affinity Designer
│   │   ├── Publisher 2/          # Affinity Publisher
│   │   └── Affinity/             # Affinity V3 (Unified)
│   └── windows/system32/
│       └── WinMetadata/          # Windows metadata files
└── vkd3d_dlls/                   # OpenCL support DLLs
```

### Key Components

**1. PyQt6 GUI Installer** (`AffinityScripts/AffinityLinuxInstaller.py`)
- Primary user-facing tool (3700+ lines)
- Handles full installation workflow: dependencies → Wine → Affinity apps
- Features: real-time status detection, DPI scaling, WebView2 runtime management
- Uses threading for non-blocking operations
- All Wine commands run with `WINEPREFIX=~/.AffinityLinux` environment variable

**2. Legacy Shell Scripts** (`AffinityScripts/*.sh`)
- Individual installers per application (Photo, Designer, Publisher, V3)
- All-in-one bash installer (`AffinityLinuxInstaller.sh`)
- Distribution detection and automatic dependency installation
- Updater script for in-place upgrades

**3. Critical Setup Steps**
- **Wine Environment**: Downloads ElementalWarriorWine, extracts to `~/.AffinityLinux`
- **WinMetadata**: Windows system files from archive.org, frequently reinstalled to prevent corruption during Affinity updates
- **vkd3d-proton**: DirectX 12 → Vulkan translation layer enabling OpenCL (v2.14.1)
- **Winetricks Dependencies**: .NET Framework 3.5/4.8, Visual C++ 2022, MSXML, Windows fonts
- **WebView2 Runtime**: Required for Affinity V3 unified app's Help system (v109.0.1518.78, runs in Windows 7 compatibility mode)

### OpenCL Hardware Acceleration

OpenCL is enabled by:
1. Installing GPU-specific OpenCL drivers on Linux (e.g., `opencl-nvidia`)
2. Setting up vkd3d-proton in Wine environment
3. Copying `d3d12.dll` and `d3d12core.dll` into each Affinity application directory
4. Configuring Wine renderer to Vulkan (via registry: `HKEY_CURRENT_USER\Software\Wine\Direct3D`)

## Development Commands

### Running the GUI Installer

```bash
# From repository root
python AffinityScripts/AffinityLinuxInstaller.py

# Or run directly from GitHub (as users do)
curl -sSL https://raw.githubusercontent.com/ryzendew/AffinityOnLinux/refs/heads/main/AffinityScripts/AffinityLinuxInstaller.py | python3
```

### Testing Individual Shell Scripts

```bash
# Test individual app installer
bash AffinityScripts/AffinityPhoto.sh

# Test all-in-one installer
bash AffinityScripts/AffinityLinuxInstaller.sh

# Test updater
bash AffinityScripts/AffinityUpdater.sh
```

### Working with Wine Environment

```bash
# Set WINEPREFIX for manual Wine commands
export WINEPREFIX=~/.AffinityLinux

# Use custom Wine build
~/.AffinityLinux/ElementalWarriorWine/bin/wine <command>

# Open Wine configuration
~/.AffinityLinux/ElementalWarriorWine/bin/winecfg

# Run Winetricks
WINEPREFIX=~/.AffinityLinux winetricks
```

### Testing Changes

```bash
# Verify Python syntax (GUI installer)
python -m py_compile AffinityScripts/AffinityLinuxInstaller.py

# Check shell script syntax (legacy installers)
bash -n AffinityScripts/AffinityLinuxInstaller.sh

# Test distribution detection
source /etc/os-release && echo "ID: $ID, VERSION: $VERSION_ID"
```

## Code Patterns and Conventions

### Distribution Detection

Both Python and Bash scripts normalize distribution IDs (e.g., "pika" → "pikaos"):

```python
# Python
with open("/etc/os-release", "r") as f:
    for line in f:
        if line.startswith("ID="):
            distro = line.split("=", 1)[1].strip().strip('"').lower()
            if distro == "pika":
                distro = "pikaos"
```

### Dependency Management

Unsupported distributions (Ubuntu, Linux Mint, Pop!_OS, Zorin) display warnings but allow continuation. Supported distributions auto-install missing packages.

Package mapping examples:
- **Arch-based**: `pacman -S python-pyqt6 wine winetricks`
- **Fedora/Nobara**: `dnf install python3-pyqt6 wine winetricks`
- **PikaOS**: `apt install python3-pyqt6 wine winetricks`
- **openSUSE**: `zypper install python313-PyQt6 wine winetricks`

### GUI Threading Pattern

Long-running operations use background threads with signal-based updates:

```python
def button_clicked(self):
    threading.Thread(target=self._operation_thread, daemon=True).start()

def _operation_thread(self):
    self.log_signal.emit("Starting operation...", "info")  # Thread-safe logging
    # Do work...
    self.show_message_signal.emit("Done", "Success!", "info")
```

### Wine Registry Modifications

Always use `regedit` with `.reg` files, not direct registry editing:

```python
reg_file = Path(self.directory) / "temp.reg"
with open(reg_file, "w") as f:
    f.write("Windows Registry Editor Version 5.00\n\n")
    f.write("[HKEY_CURRENT_USER\\Software\\Wine\\Direct3D]\n")
    f.write('"renderer"="vulkan"\n')

self.run_command([str(regedit), str(reg_file)], env=env)
reg_file.unlink()
```

## Known Issues and Workarounds

### WinMetadata Corruption

**Problem**: Affinity installers may corrupt Windows metadata files during installation/update.

**Solution**: Always reinstall WinMetadata after running Affinity installers. Both GUI and shell scripts do this automatically.

### WebView2 Runtime for Affinity V3

**Problem**: Affinity V3 requires WebView2 to enable Help → View Help functionality.

**Solution**: 
1. Install WebView2 v109.0.1518.78 in Windows 7 compatibility mode
2. After installation, set global Wine version back to Windows 11
3. Configure `msedgewebview2.exe` specifically to run as Windows 7 via registry
4. Disable Edge auto-update services via registry

### GLIBC Version Conflicts

**Problem**: `wine: could not load ntdll.so: libc.so.6: version GLIBC_2.38 not found`

**Cause**: ElementalWarriorWine requires GLIBC 2.38+, which older distributions lack.

**Resolution**: Use modern distributions (see README supported list) or build Wine manually.

### PikaOS Wine Compatibility

PikaOS ships with incompatible Wine. The installer automatically prompts users to replace it with WineHQ staging before proceeding.

## Distribution-Specific Notes

### Officially Supported
PikaOS 4, CachyOS, Nobara, Arch Linux, EndeavourOS, XeroLinux, Fedora, openSUSE (Tumbleweed/Leap)

### Not Officially Supported (Manual Dependencies)
Ubuntu, Linux Mint, Pop!_OS, Zorin OS - marked as "OUT OF DATE" by scripts due to package management limitations

### Arch-based Python Package Installation

Arch-based distributions require `--break-system-packages` flag for pip due to PEP 668. The GUI installer handles this automatically when installing PyQt6.

## File Structure

```
AffinityScripts/
├── AffinityLinuxInstaller.py    # Main GUI installer (3700+ lines)
├── AffinityLinuxInstaller.sh    # Legacy all-in-one bash installer
├── AffinityPhoto.sh             # Individual Affinity Photo installer
├── AffinityDesigner.sh          # Individual Affinity Designer installer
├── AffinityPublisher.sh         # Individual Affinity Publisher installer
├── Affinityv3.sh                # Individual Affinity V3 installer
├── AffinityUpdater.sh           # Update existing installations
└── AffinityWine10.17.sh         # Wine 10.17 setup script

Guide/
└── GUI-Installer-Guide.md       # Detailed GUI usage instructions

icons/                           # Application icons
wine-dark-theme.reg              # Wine dark theme registry settings
```

## Modifying Installers

### Adding Support for New Distributions

1. Update `detect_distro()` function in both Python and Bash
2. Add package manager commands in dependency installation logic
3. Test on target distribution with all dependency variations

### Updating Wine Version

1. Change Wine download URL in `setup_wine()` / setup functions
2. Update `ElementalWarriorWine` symlink logic if directory naming changes
3. Test Wine compatibility with all Affinity versions

### Updating vkd3d-proton Version

1. Change version in `setup_vkd3d()`: URL, filename, extraction paths
2. Verify OpenCL functionality after change (check in Affinity Preferences → Performance)

### Updating WebView2 Runtime

1. Modify download URL in `install_webview2_runtime()` / `_install_webview2_runtime_thread()`
2. Test Help → View Help functionality in Affinity V3 after update
3. Ensure compatibility settings (Windows 7 mode, disabled updates) still work

## Testing Checklist

When making changes:
- [ ] Test on at least one Arch-based and one Fedora-based distribution
- [ ] Verify distribution detection works correctly
- [ ] Confirm dependency auto-installation succeeds
- [ ] Check Wine environment setup creates all required directories
- [ ] Test one full Affinity app installation (Photo, Designer, Publisher, or V3)
- [ ] Verify OpenCL is enabled in Affinity (Preferences → Performance)
- [ ] For Affinity V3: confirm WebView2 installed and Help → View Help works
- [ ] Test update functionality with existing installation
- [ ] Confirm desktop entries created correctly in `~/.local/share/applications/`
