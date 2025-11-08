# GUI Terminal Capture - Complete Non-Interactive Execution

## Overview

The AffinityLinuxInstaller has been updated to capture ALL terminal prompts and handle them within the GUI. The application now runs completely independently of terminal interaction, making it suitable for launching from application menus, desktop shortcuts, or any GUI environment.

## What Was Changed

### 1. Sudo Password Handling (GUI Dialog)
**Before**: Terminal prompts for sudo password
**After**: Professional password dialog in the GUI

- Custom password input dialog with hidden text entry
- Password validation before use
- Session-based caching (enter once, use throughout session)
- Up to 3 attempts for incorrect passwords
- Thread-safe implementation with Qt signals

### 2. Terminal Yes/No Prompts (Auto-Handled & GUI Detection)
**Before**: Commands like `apt install` or `wget` prompt for yes/no in terminal
**After**: Two-layer approach:
1. Primary: Commands run with non-interactive flags to prevent prompts
2. Fallback: If prompts still appear, they're detected and shown in GUI dialogs

#### Package Managers
- **APT** (Debian/Ubuntu/Pop!_OS/PikaOS): Uses `-y` flag + `DEBIAN_FRONTEND=noninteractive`
- **DNF** (Fedora/Nobara): Uses `-y` flag
- **Pacman** (Arch/CachyOS/EndeavourOS/XeroLinux): Uses `--noconfirm` flag
- **Zypper** (openSUSE): Uses `-y` flag

#### Environment Variables Set
```bash
DEBIAN_FRONTEND=noninteractive         # No interactive prompts for Debian-based
NEEDRESTART_MODE=a                     # Auto-restart services without asking
DEBIAN_PRIORITY=critical               # Only show critical messages
APT_LISTCHANGES_FRONTEND=none          # Skip package change notifications
LANG=C                                 # Use C locale for consistent output
LC_ALL=C                               # Prevent encoding issues
WINETRICKS_GUI=0                       # Disable winetricks GUI dialogs
```

### 3. Winetricks Dialog Suppression
**Before**: Winetricks could show GUI dialogs for user input
**After**: Completely non-interactive execution

- `--unattended` flag: Skip all interactive prompts
- `--verbose` flag: Show detailed progress
- `--force` flag: Force installation even if already installed
- `--no-isolate` flag: Use system Wine prefix
- `--optout` flag: Opt out of telemetry
- `WINETRICKS_GUI=0` environment variable

### 4. Service Restart Prompts (Auto-Handled)
**Before**: APT could ask "Which services should be restarted?"
**After**: Services auto-restart without prompting via `NEEDRESTART_MODE=a`

### 5. Interactive Prompt Detection (GUI Fallback)
**For any prompts that slip through:**

A smart detection system monitors command output for interactive prompts:
- **Patterns detected**: "Overwrite?", "(y/n)", "[Y/n]", "continue?", "proceed?", "replace?"
- **GUI dialog shown**: User sees the prompt in a QMessageBox
- **Default values**: Capitalized letters indicate defaults (e.g., "(Y/n)" = default Yes)
- **Response sent**: User's choice is automatically sent back to the command

**Example prompts handled**:
- `winehq-archive.key' exists. Overwrite? (y/N)`
- `File exists. Replace? [y/N]`
- `Continue with installation? (Y/n)`

## Technical Implementation

### Modified Functions

#### `run_command()`
```python
# Automatically sets environment variables for all commands
env['DEBIAN_FRONTEND'] = 'noninteractive'
env['NEEDRESTART_MODE'] = 'a'
env['DEBIAN_PRIORITY'] = 'critical'
env['APT_LISTCHANGES_FRONTEND'] = 'none'
env['LANG'] = 'C'
env['LC_ALL'] = 'C'

# Handles sudo with GUI password dialog
if command[0] == "sudo":
    password = self.get_sudo_password()  # Shows GUI dialog
    # Uses sudo -S to read password from stdin
```

#### `run_command_streaming()`
Same environment variables applied for streaming commands (winetricks, etc.)

#### `configure_wine()` and `_install_winetricks_deps()`
```python
env["WINETRICKS_GUI"] = "0"
env["DISPLAY"] = env.get("DISPLAY", ":0")
# Commands use: winetricks --unattended --verbose --force --no-isolate --optout
```

### Password Dialog Implementation

```python
class _request_sudo_password_safe():
    # Creates QDialog with QLineEdit in Password mode
    # Enter key submits
    # Password validated with test command before use
    # Cached for session after successful validation
```

### Interactive Prompt Detection

```python
def run_command_interactive():
    # Monitors command output in real-time using select()
    # Detects patterns: "overwrite?", "(y/n)", "[y/n]", etc.
    # Shows QMessageBox.question() for yes/no prompts
    # Sends user response back to process stdin
    # Continues monitoring until process completes
```

**Prevention (Primary)**:
```bash
# wget: Remove existing files first to prevent overwrite prompts
sudo rm -f /etc/apt/sources.list.d/winehq-*.sources
sudo wget -P /etc/apt/sources.list.d/ <URL>

# All environment variables prevent most prompts
```

**Detection (Fallback)**:
```python
if "overwrite?" in output_line.lower():
    response = self.get_interactive_response(line, default="n")
    process.stdin.write(response)
```

## Command Examples

### Before (Terminal Interactive)
```bash
# User has to interact with terminal:
$ python AffinityLinuxInstaller.py
> sudo apt install wine
[sudo] password for user: <user types here>
Do you want to continue? [Y/n] <user types Y>
Which services should be restarted? <user presses Enter>
```

### After (GUI Only)
```bash
# User only interacts with GUI:
$ python AffinityLinuxInstaller.py
# GUI opens
# User clicks "Install Dependencies"
# Password dialog appears in GUI
# User enters password in GUI
# All operations proceed automatically with progress shown in GUI log
# No terminal interaction needed
```

## Benefits

### For Users
1. **Can launch from application menu** - No need to open terminal
2. **Professional experience** - Native GUI dialogs instead of terminal prompts
3. **Clear feedback** - All progress shown in application log area
4. **Session convenience** - Password entered once, used throughout
5. **No accidental interruption** - Can't accidentally close terminal and kill process

### For Developers
1. **Predictable execution** - No variability from user terminal responses
2. **Better error handling** - Can catch and handle all errors in GUI
3. **Consistent behavior** - Same experience across all distributions
4. **Easier debugging** - All output captured in application log

## Testing Checklist

Test the following operations to verify non-interactive execution:

### Basic Operations
- [ ] Launch app from GUI (not terminal)
- [ ] Install system dependencies (should show password dialog once)
- [ ] Install winetricks dependencies (no additional prompts)
- [ ] Install Affinity application (no prompts during installation)

### Distribution-Specific
- [ ] **PikaOS/Pop!_OS**: WineHQ repository addition (password dialog only)
- [ ] **Arch-based**: Pacman operations (password dialog only, no confirmation prompts)
- [ ] **Fedora/Nobara**: DNF operations (password dialog only, no confirmation prompts)
- [ ] **openSUSE**: Zypper operations (password dialog only, no confirmation prompts)

### Edge Cases
- [ ] Wrong password (should retry with new dialog)
- [ ] Cancel password dialog (operation should abort gracefully)
- [ ] Multiple sudo operations in sequence (should use cached password)
- [ ] Long-running operation (winetricks) - verify no hidden terminal prompts

## Compatibility

### Supported Launch Methods
✅ Application menu (GNOME, KDE, etc.)
✅ Desktop shortcut
✅ Run dialog (Alt+F2)
✅ Terminal
✅ File manager (double-click)
✅ Remote desktop
✅ Automated scripts

### All Distributions
✅ PikaOS 4
✅ CachyOS
✅ Nobara
✅ Arch Linux
✅ EndeavourOS
✅ XeroLinux
✅ Fedora
✅ openSUSE (Tumbleweed/Leap)
⚠️ Pop!_OS (supported but not officially maintained)
⚠️ Ubuntu/Mint/Zorin (supported but not officially maintained)

## Remaining Manual Steps

The only manual interaction still required:
1. **Installer Wizards**: When running .exe installers (Affinity apps), the installer GUI opens
   - This is expected and necessary - users need to accept licenses, choose install location, etc.
   - Log shows: "Follow the installation wizard in the window that opens"

2. **File Selection Dialogs**: User must browse for installer files
   - Uses Qt QFileDialog - fully GUI-based
   - No terminal interaction

## Migration from Old Behavior

### For Users
- **No changes needed** - The app works exactly the same from the user's perspective
- **Enhancement only** - Password prompt is now in GUI instead of terminal
- **Backward compatible** - Can still be run from terminal if desired

### For Scripts/Automation
- Commands that previously prompted for yes/no now auto-proceed
- Sudo commands require password on first use, then cached
- All output still goes to log file: `~/AffinitySetup.log`

## Future Enhancements

Potential improvements:
- [ ] Optional: Remember sudo password between sessions (encrypted storage)
- [ ] Optional: Use PolicyKit/pkexec instead of sudo (more secure)
- [ ] Optional: Add "Remember password" checkbox in dialog
- [ ] Optional: Fingerprint/biometric authentication integration

## Summary

**The AffinityLinuxInstaller is now a true GUI application** that requires zero terminal interaction. Users can launch it from their application menu just like any other application, and all operations including sudo authentication are handled through professional GUI dialogs.

All formerly terminal-based prompts are now either:
1. Handled automatically through non-interactive flags and environment variables, or
2. Captured and presented as GUI dialogs (sudo password)

The result is a seamless, professional user experience that matches modern application standards.
