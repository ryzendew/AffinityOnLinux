# GUI Sudo Password Authentication Update

## Overview

The AffinityLinuxInstaller GUI has been updated to prompt for sudo passwords within the application interface instead of requiring terminal interaction. This provides a more user-friendly experience and eliminates the need to run the installer from a terminal.

## Changes Made

### 1. Non-Interactive Terminal Execution
All commands now run in non-interactive mode, preventing terminal prompts:
- **Environment Variables**: Set `DEBIAN_FRONTEND=noninteractive`, `NEEDRESTART_MODE=a`, and others
- **Package Manager Flags**: Already using `-y`, `--noconfirm`, etc.
- **Winetricks**: Set `WINETRICKS_GUI=0` to prevent GUI dialogs, using `--unattended` flag
- **APT**: Configured to skip service restart prompts and package change notifications

### 2. New Password Dialog
- Added a secure password input dialog that appears when sudo authentication is required
- Dialog includes:
  - Clear explanation of why authentication is needed
  - Password field with hidden input (echo mode)
  - OK/Cancel buttons
  - Enter key support for quick submission

### 2. Password Validation and Caching
- **Password Validation**: The entered password is tested with a harmless `sudo -S true` command before use
- **Password Caching**: Once validated, the password is cached for the session to avoid repeated prompts
- **Multiple Attempts**: Users get up to 3 attempts to enter the correct password
- **Security**: Password is stored in memory only during the session and cleared when the application closes

### 3. Updated Command Execution
The `run_command()` method now:
- Automatically detects when a command requires sudo
- Prompts for password via the GUI when needed
- Uses `sudo -S` flag to read password from stdin
- Provides clear feedback on authentication success/failure

### 4. Special Handling for GPG Operations
Updated both PikaOS and Pop!_OS dependency installation to handle GPG key operations:
- These operations pipe key data to `sudo gpg`
- Password is sent first via stdin, followed by the key data
- Properly handles the combined input stream

## Technical Details

### New Class Variables
```python
self.sudo_password = None  # Cached sudo password
self.sudo_password_validated = False  # Whether password has been validated
```

### New Methods
- `_request_sudo_password_safe()`: Creates and displays the password dialog (runs in main thread)
- `get_sudo_password()`: Thread-safe method to request password with timeout
- `validate_sudo_password()`: Tests password validity before use

### New Signal
```python
sudo_password_signal = pyqtSignal()  # Signal to request sudo password
```

## User Experience

### Before
1. User runs installer from terminal
2. Terminal prompts for password when needed
3. User enters password in terminal
4. Installation continues

### After
1. User runs installer (from GUI or terminal)
2. GUI shows password dialog when sudo is needed
3. User enters password in GUI
4. Password is validated immediately
5. Installation continues with cached password
6. No more prompts for the rest of the session

## Affected Operations

The following operations now run fully in the GUI without terminal interaction:

1. **Dependency Installation** (all distributions)
   - Package manager commands: `pacman -S --noconfirm`, `dnf install -y`, `zypper install -y`, `apt install -y`
   - No terminal prompts for yes/no confirmation
   - Service restart handled automatically without prompting
   
2. **PikaOS Configuration**
   - Creating APT keyrings directory (GUI password prompt only)
   - Adding WineHQ GPG key (GUI password prompt only)
   - Adding i386 architecture (non-interactive)
   - Repository configuration (non-interactive)
   - Package installation (non-interactive with DEBIAN_FRONTEND=noninteractive)

3. **Pop!_OS Configuration**
   - Creating APT keyrings directory (GUI password prompt only)
   - Adding WineHQ GPG key (GUI password prompt only)
   - Adding i386 architecture (non-interactive)
   - Repository configuration (non-interactive)
   - Package installation (non-interactive with DEBIAN_FRONTEND=noninteractive)

4. **Winetricks Operations**
   - All winetricks commands run with `--unattended` and `WINETRICKS_GUI=0`
   - No GUI dialogs from winetricks itself
   - Progress shown in main application log
   - Components: .NET Framework, fonts, Visual C++, MSXML, etc.

## Security Considerations

- Password is only stored in memory during the session
- Password input field uses hidden echo mode (shows bullets instead of text)
- Password is validated before use to avoid security issues
- Failed authentication provides clear error messages
- Users can cancel authentication at any time

## Testing

To test the changes:

1. Run the installer: `python AffinityScripts/AffinityLinuxInstaller.py`
2. Click "Check Dependencies"
3. If dependencies are missing, click "Install Dependencies"
4. Password dialog should appear
5. Enter your password and verify:
   - Correct password: Installation proceeds
   - Wrong password: Error message appears, retry available
   - Cancel: Operation is cancelled gracefully

## Compatibility

- Works on all supported distributions
- No changes to CLI behavior for non-sudo commands
- Backward compatible with existing functionality
- No new dependencies required (uses existing PyQt6)

## Notes

- The password dialog appears only when sudo commands are executed
- Password is cleared when the application closes
- If the password becomes invalid during the session (e.g., sudo timeout), a new prompt will appear
- The implementation is thread-safe and works with the existing threading model
