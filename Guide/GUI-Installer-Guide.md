# Affinity Linux Installer - GUI Guide

This guide explains how to use the Python GUI installer for Affinity software on Linux. The installer provides a user-friendly graphical interface to set up and install Affinity applications.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Button Reference](#button-reference)
4. [Step-by-Step Workflows](#step-by-step-workflows)
5. [Understanding the Log Output](#understanding-the-log-output)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The GUI installer is a graphical application that helps you:
- Set up Wine (a compatibility layer to run Windows software)
- Install system dependencies automatically
- Download and install Affinity applications
- Configure hardware acceleration (OpenCL)
- Manage and update your Affinity installations

**The installer window has:**
- **Button sections** on the left side (organized by function)
- **Log output** on the right side (shows what's happening)
- **Status information** at the bottom

---

## Getting Started

### Starting the Installer

1. Open a terminal
2. Navigate to the installer directory:
   ```bash
   cd ~/.config/AffinityOnLinux/AffinityScripts
   ```
3. Run the Python installer:
   ```bash
   python3 AffinityLinuxInstaller.py
   ```

The GUI window will open. You'll see several button sections on the left and a log area on the right.

---

## Button Reference

### Quick Start Section

#### **One-Click Full Setup**
The easiest way to get started! This button does everything automatically:
1. Detects your Linux distribution
2. Checks and installs all required system packages
3. Downloads and sets up Wine
4. Installs Windows components (.NET, fonts, etc.)
5. Configures everything for Affinity
6. Asks if you want to install an Affinity app

**When to use:** If this is your first time installing, or you want a fresh setup.

**Time required:** 10-30 minutes (depends on internet speed)

---

### System Setup Section

These buttons handle the setup process step-by-step. Use them if you prefer manual control or need to fix something.

#### **Setup Wine Environment**
Downloads and configures the custom Wine build needed to run Affinity software.

**What it does:**
- Downloads Wine binaries
- Sets up the Wine environment in `~/.AffinityLinux`
- Downloads and installs Windows metadata files
- Sets up OpenCL support (vkd3d-proton)
- Configures Wine for Windows 11 compatibility

**When to use:** When you need Wine set up but don't want to do the full setup.

**Time required:** 5-10 minutes

#### **Install System Dependencies**
Installs required Linux packages on your system (wine, winetricks, wget, curl, etc.).

**What it does:**
- Checks which packages are missing
- Installs them using your distribution's package manager
- Shows progress in the log

**When to use:** If you get dependency errors or want to install packages manually.

**Time required:** 1-5 minutes (may ask for your password)

#### **Install Winetricks Dependencies**
Installs Windows components needed by Affinity (like .NET Framework, fonts, Visual C++).

**What it does:**
- Installs .NET Framework 3.5 and 4.8
- Installs Windows core fonts
- Installs Visual C++ Redistributables
- Installs MSXML libraries
- Configures Vulkan renderer

**When to use:** If Affinity complains about missing Windows components.

**Time required:** 10-20 minutes

#### **Reinstall WinMetadata**
Re-downloads and installs Windows metadata files (may get corrupted during Affinity installation).

**What it does:**
- Removes old metadata files
- Downloads fresh Windows metadata from archive.org
- Extracts them to the Wine environment

**When to use:** If you get errors about missing Windows components or metadata corruption.

**Time required:** 2-5 minutes

#### **Download Affinity Installer**
Downloads the Affinity installer file to your computer.

**What it does:**
- Opens a file save dialog
- Downloads `Affinity x64.exe` from Affinity Studio
- Saves it where you choose (defaults to Downloads folder)
- Shows download progress

**When to use:** When you want to download the installer separately, or prepare it for later.

**Time required:** 2-10 minutes (depends on internet speed)

**Note:** You can use this downloaded file with "Install from File Manager" later.

#### **Install from File Manager**
Install any Windows program (.exe file) using the custom Wine setup.

**What it does:**
- Opens a file dialog to select an .exe file
- Asks for the application name
- Runs the installer through Wine
- Creates a desktop entry for the app

**When to use:** When you have an installer file already downloaded, or want to install non-Affinity software.

---

### Update Affinity Applications Section

These buttons let you update existing Affinity installations.

#### **Affinity (Unified)**, **Affinity Photo**, **Affinity Designer**, **Affinity Publisher**
Updates the corresponding Affinity application to a newer version.

**What it does:**
- Asks you to select the new installer .exe file
- Runs the installer (updates existing installation)
- Reinstalls WinMetadata (to prevent corruption)
- For Affinity v3 (Unified), reinstalls settings files

**When to use:** When a new version of Affinity is released and you want to update.

**Time required:** 5-15 minutes

**Note:** These buttons only work if the application is already installed. If a button is disabled (grayed out), that app isn't installed yet.

---

### Troubleshooting Section

These tools help fix common issues.

#### **Open Wine Configuration**
Opens the Wine configuration tool (winecfg) using your custom Wine setup.

**What it does:**
- Launches the Wine configuration GUI
- Lets you adjust Wine settings, Windows version, graphics, etc.

**When to use:** If you need to change Wine settings manually, troubleshoot graphics issues, or configure libraries.

#### **Set Windows 11 + Renderer**
Sets the Windows version to Windows 11 and configures the graphics renderer.

**What it does:**
- Sets Wine to Windows 11 mode
- Lets you choose between Vulkan (recommended) or OpenGL renderer
- Applies the configuration

**When to use:** If OpenCL/hardware acceleration isn't working, or you're having graphics issues.

**Renderer options:**
- **Vulkan (Recommended)**: Better performance, enables OpenCL support
- **OpenGL (Alternative)**: Fallback option if Vulkan doesn't work

#### **Fix Settings**
Installs Affinity v3 settings files to enable settings saving.

**What it does:**
- Downloads settings files from the repository
- Copies them to the correct location in the Wine environment
- Only works for Affinity v3 (Unified application)

**When to use:** If Affinity v3 doesn't save your preferences/settings.

**Note:** This only works for Affinity v3 (Unified). It won't help with Photo/Designer/Publisher v2.

---

### Other Section

#### **Special Thanks**
Shows credits for contributors to the project.

#### **Exit**
Closes the installer window.

---

## Step-by-Step Workflows

### Workflow 1: First-Time Installation (Easiest)

**Goal:** Install Affinity for the first time with minimal steps.

**Steps:**
1. Start the installer (see [Getting Started](#getting-started))
2. Click **"One-Click Full Setup"**
3. Wait for the setup to complete (watch the log for progress)
4. When prompted, choose **"Yes"** to install an Affinity application
5. Select which app you want (e.g., "Affinity (Unified)")
6. Choose **"Download from Affinity Studio (automatic)"** and click OK
7. Wait for the download and installation
8. Done! Your app should appear in your application menu

**Total time:** 15-40 minutes

---

### Workflow 2: Manual Step-by-Step Installation

**Goal:** Install Affinity manually with full control over each step.

**Steps:**
1. Start the installer
2. Click **"Install System Dependencies"** → Wait for completion
3. Click **"Setup Wine Environment"** → Wait for completion
4. Click **"Install Winetricks Dependencies"** → Wait for completion
5. Download the installer:
   - Option A: Click **"Download Affinity Installer"** → Choose save location → Wait
   - Option B: Download manually from https://downloads.affinity.studio/Affinity%20x64.exe
6. Click **"Install from File Manager"** → Select the downloaded .exe file → Enter app name
7. Follow the installer wizard that opens
8. Done!

**Total time:** 20-45 minutes

---

### Workflow 3: Installing Affinity v3 (Unified)

**Goal:** Install the new unified Affinity application.

**Steps:**
1. Complete setup (use "One-Click Full Setup" or manual steps)
2. Click **"One-Click Full Setup"** and when prompted, select **"Affinity (Unified)"**
   - OR use **"Install from File Manager"** if you have the installer
3. Choose download or provide your own installer
4. After installation completes, click **"Fix Settings"** to enable settings saving
5. Done! Launch Affinity from your application menu

**Note:** The unified app requires the settings fix to save preferences properly.

---

### Workflow 4: Updating an Existing Installation

**Goal:** Update Affinity Photo/Designer/Publisher to a new version.

**Steps:**
1. Download the new installer:
   - Click **"Download Affinity Installer"** → Save it
   - OR download manually from your Affinity account
2. Click the appropriate update button (e.g., **"Affinity Photo"**)
3. Select the new installer .exe file you downloaded
4. Wait for the update to complete
5. Done! Your app is updated

**Note:** The update process preserves your existing settings and files.

---

### Workflow 5: Fixing Settings Issues (Affinity v3)

**Goal:** Make Affinity v3 save your settings properly.

**Steps:**
1. Make sure Affinity v3 is installed
2. Click **"Fix Settings"**
3. Wait for the settings files to install
4. Launch Affinity v3 and check if settings save

**Note:** You may need to restart Affinity for changes to take effect.

---

### Workflow 6: Fixing OpenCL/Hardware Acceleration

**Goal:** Enable GPU acceleration if it's not working.

**Steps:**
1. Click **"Set Windows 11 + Renderer"**
2. Select **"Vulkan (Recommended - OpenCL support)"**
3. Click OK and wait for configuration
4. Restart Affinity and check:
   - Affinity → Preferences → Performance → Hardware Acceleration

**Note:** If Vulkan doesn't work, try OpenGL as an alternative.

---

## Understanding the Log Output

The log area on the right side of the window shows what's happening. Here's what different message types mean:

### Message Types

- **[INFO]** - General information about what's happening
- **[SUCCESS]** or **✓** - Something completed successfully
- **[WARNING]** or **⚠** - Something went wrong but it's not critical
- **[ERROR]** or **✗** - Something failed

### What to Look For

**Good signs:**
- Messages ending with "✓ ... installed" or "completed"
- Progress percentages increasing
- "Download completed" messages
- "Installation completed" messages

**Warning signs:**
- Many "[WARNING]" messages (might be okay, but pay attention)
- "Failed to..." messages
- Errors that stop the process

**Action required:**
- If you see errors that stop installation, check the error message
- Try running the failed step again
- Check the [Troubleshooting](#troubleshooting) section

### Log Sections

The log is divided by separator lines (━━━━━━━━━━━━━━━━). Each section represents a different operation (e.g., "Wine Binary Setup", "Affinity Photo Installation").

---

## Troubleshooting

### Problem: "Wine is not set up yet"

**Solution:** Click **"Setup Wine Environment"** first and wait for it to complete.

---

### Problem: "Missing dependencies" errors

**Solution:** Click **"Install System Dependencies"**. If it fails, you may need to install packages manually using your package manager.

---

### Problem: Download fails or is slow

**Solutions:**
- Check your internet connection
- Try clicking the download button again
- Use **"Download Affinity Installer"** to download separately, then use **"Install from File Manager"**
- Download manually from https://downloads.affinity.studio/Affinity%20x64.exe

---

### Problem: Installation wizard doesn't open

**Solutions:**
- Wait a few seconds (it may take time to start)
- Check the log for errors
- Make sure Wine is fully set up
- Try running the installer again

---

### Problem: OpenCL/Hardware Acceleration not working

**Solutions:**
1. Click **"Set Windows 11 + Renderer"** → Choose Vulkan
2. Make sure you have Vulkan drivers installed on your system
3. Check Affinity Preferences → Performance → Hardware Acceleration
4. If still not working, try OpenGL renderer

---

### Problem: Affinity v3 doesn't save settings

**Solution:** Click **"Fix Settings"** to install the settings files.

---

### Problem: Update buttons are grayed out

**Solution:** Those apps aren't installed yet. Install them first using **"One-Click Full Setup"** or **"Install from File Manager"**.

---

### Problem: "Permission denied" errors

**Solutions:**
- Some operations require your password (sudo) - enter it when prompted
- Make sure you have write permissions in `~/.AffinityLinux`

---

### Problem: Installation hangs or freezes

**Solutions:**
- Wait 5-10 minutes (some operations take a long time)
- Check the log - it should show progress
- If truly frozen, close and restart the installer
- Try the manual step-by-step workflow instead

---

### Problem: Application doesn't appear in menu after installation

**Solutions:**
- Refresh your application menu (log out and back in, or restart)
- Check `~/.local/share/applications/` for desktop files
- Try launching from terminal to see error messages

---

## Tips for Success

1. **Read the log:** The log tells you what's happening. Pay attention to it.
2. **Be patient:** Some operations take 10-20 minutes. Don't close the installer.
3. **Complete one step at a time:** Don't click multiple buttons simultaneously.
4. **Use "One-Click Full Setup" first:** It's the easiest way for beginners.
5. **Keep installer open:** Don't close the installer window until everything is done.
6. **Check requirements:** Make sure you're on a supported Linux distribution.

---

## Getting Help

If you're still having issues:
1. Read the log output carefully - it often contains helpful error messages
2. Check that you're on a supported distribution
3. Make sure all dependencies are installed
4. Try the troubleshooting steps above
5. Check the main README.md for additional information

---

## Quick Reference Card

| Button | When to Use | Time |
|--------|-------------|------|
| **One-Click Full Setup** | First time installation | 15-40 min |
| **Setup Wine Environment** | Wine not set up | 5-10 min |
| **Install System Dependencies** | Missing packages | 1-5 min |
| **Install Winetricks Dependencies** | Missing Windows components | 10-20 min |
| **Download Affinity Installer** | Want installer file | 2-10 min |
| **Install from File Manager** | Have installer file | 5-15 min |
| **Update [App Name]** | Update existing app | 5-15 min |
| **Set Windows 11 + Renderer** | OpenCL not working | 1 min |
| **Fix Settings** | Affinity v3 won't save settings | 2-5 min |

---

**Last Updated:** This guide covers the GUI installer as of the latest version.

