# OpenCL Hardware Acceleration Guide

This guide explains how to set up OpenCL hardware acceleration for Affinity applications on Linux. OpenCL enables GPU-accelerated processing for improved performance in Affinity Photo, Designer, and Publisher.

## Prerequisites

- AffinityOnLinux installer has been run and Affinity applications are installed
- Your GPU drivers are properly installed
- You have administrator (sudo) access

## GPU Compatibility

**NVIDIA GPUs:** ✅ OpenCL works well with proper driver installation. No known issues.

**AMD GPUs:** ⚠️ OpenCL may have compatibility issues. If you experience problems, consider using vkd3d-proton or DXVK instead (see [Hardware Acceleration](HARDWARE-ACCELERATION.md)).

**Intel GPUs:** ⚠️ OpenCL may have compatibility issues. If you experience problems, consider using vkd3d-proton or DXVK instead (see [Hardware Acceleration](HARDWARE-ACCELERATION.md)).

## Installation

### Step 1: Install OpenCL Drivers

Install the appropriate OpenCL drivers for your GPU and distribution:

#### Arch Linux (NVIDIA)

```bash
sudo pacman -S opencl-nvidia
```

#### Arch Linux (AMD)

```bash
sudo pacman -S opencl-amd apr apr-util
yay -S libxcrypt-compat
```

#### Fedora/Nobara (AMD)

```bash
sudo dnf install rocm-opencl apr apr-util zlib libxcrypt-compat libcurl libcurl-devel mesa-libGLU -y
```

### Step 2: Verify OpenCL Installation

After installing the drivers, verify that OpenCL is detected:

```bash
# Check if OpenCL devices are available
clinfo
```

If `clinfo` is not installed, you can install it:

**Arch Linux:**
```bash
sudo pacman -S clinfo
```

**Fedora/Nobara:**
```bash
sudo dnf install clinfo
```

### Step 3: Configure Affinity Applications

The AffinityOnLinux installer automatically configures vkd3d-proton for OpenCL support. The necessary DLLs (`d3d12.dll` and `d3d12core.dll`) are automatically copied to each Affinity application directory during installation.

## Verification

To verify that OpenCL is working in Affinity applications:

1. Launch any Affinity application (Photo, Designer, or Publisher)
2. Go to **Edit → Preferences → Performance**
3. Check the **Hardware Acceleration** section
4. You should see your GPU listed and OpenCL enabled

## Troubleshooting

### OpenCL Not Detected

If OpenCL is not detected in Affinity applications:

1. Verify OpenCL drivers are installed correctly using `clinfo`
2. Ensure your GPU drivers are up to date
3. Try restarting your system after installing OpenCL drivers
4. Check that vkd3d-proton DLLs are present in the Affinity application directory:
   ```bash
   ls ~/.AffinityLinux/drive_c/Program\ Files/Affinity/*/d3d12*.dll
   ```

### Performance Issues

If you experience performance issues with OpenCL:

- Consider using vkd3d-proton or DXVK instead (automatically configured by the installer)
- Check GPU temperature and ensure adequate cooling
- Verify that your GPU is not being throttled

### AMD/Intel GPU Issues

If you have an AMD or Intel GPU and experience OpenCL issues:

- We cannot provide support for AMD/Intel GPU OpenCL issues as we do not have access to these GPUs for testing
- Use vkd3d-proton or DXVK instead, which are automatically configured by the installer
- See [Hardware Acceleration](HARDWARE-ACCELERATION.md) for more information

## Alternative: Using Lutris

If you prefer to use Lutris for managing Affinity applications:

1. Install vkd3d-proton through [ProtonPlus](https://github.com/Vysp3r/ProtonPlus)
2. Configure Lutris:
   - Open the application's configuration settings
   - Navigate to **Runner Options**
   - Select vkd3d-proton as the vkd3d version
   - Disable DXVK
3. Launch Affinity applications through Lutris

## Additional Resources

- [Hardware Acceleration Guide](HARDWARE-ACCELERATION.md) - Overview of acceleration options
- [Known Issues](Known-issues.md) - Common problems and solutions
- [GitHub Issues](https://github.com/ryzendew/AffinityOnLinux/issues) - Report problems or ask questions
