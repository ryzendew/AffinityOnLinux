# Interactive Prompt Detection and GUI Handling

## Overview

The AffinityLinuxInstaller now includes a sophisticated system for detecting and handling interactive terminal prompts through GUI dialogs. This ensures that **any** prompt that appears during command execution is shown to the user in a professional dialog, rather than being hidden or causing the command to hang.

## Two-Layer Approach

### Layer 1: Prevention (Primary Strategy)
Prevent prompts from appearing in the first place:
- Use non-interactive flags (`-y`, `--noconfirm`, etc.)
- Set environment variables (`DEBIAN_FRONTEND=noninteractive`, etc.)
- Remove existing files before overwriting (`rm -f` before `wget`)
- Use appropriate command options

### Layer 2: Detection (Fallback Strategy)
If a prompt still appears, detect and handle it via GUI:
- Real-time monitoring of command output
- Pattern matching for common prompt formats
- GUI dialog presentation to user
- Automatic response submission back to command

## How It Works

### Detection Patterns

The system watches for these patterns in command output:

```python
PROMPT_PATTERNS = [
    "overwrite?",      # File overwrite prompts
    "(y/n)",           # Yes/no questions (lowercase)
    "[y/n]",           # Yes/no questions (brackets)
    "(Y/n)",           # Yes/no with default Yes
    "(y/N)",           # Yes/no with default No
    "yes/no",          # Spelled out
    "continue?",       # Continuation prompts
    "proceed?",        # Proceed prompts
    "replace?",        # Replacement prompts
]
```

### Output Monitoring

Uses Python's `select()` to monitor process output in real-time:

```python
import select

while process_running:
    # Check stdout and stderr for new data
    readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
    
    for stream in readable:
        line = stream.readline()
        
        # Check if line contains a prompt pattern
        if detect_prompt(line):
            # Show GUI dialog and get response
            response = show_gui_dialog(line)
            # Send response to process
            process.stdin.write(response)
```

### Dialog Types

#### Yes/No Questions
For prompts containing `(y/n)`, `[Y/n]`, etc.:

```python
reply = QMessageBox.question(
    self,
    "User Input Required",
    "winehq-archive.key' exists. Overwrite? (y/N)",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    QMessageBox.StandardButton.No  # Default based on capitalization
)
```

#### General Input
For other prompts requiring text input:

```python
response, ok = QInputDialog.getText(
    self,
    "User Input Required",
    "Enter value:",
    QLineEdit.EchoMode.Normal,
    default_value
)
```

## Examples

### Example 1: File Overwrite Prompt

**Terminal Prompt** (would appear but is hidden):
```
'winehq-archive.key' exists. Overwrite? (y/N)
```

**GUI Dialog** (what user sees):
```
┌─────────────────────────────────────────┐
│        User Input Required               │
├─────────────────────────────────────────┤
│                                          │
│  'winehq-archive.key' exists.           │
│  Overwrite? (y/N)                       │
│                                          │
├─────────────────────────────────────────┤
│              [ Yes ]  [ No ]             │
│                      ^^^^^               │
│                   (default)              │
└─────────────────────────────────────────┘
```

**Log Output**:
```
  'winehq-archive.key' exists. Overwrite? (y/N)
Interactive prompt detected: 'winehq-archive.key' exists. Overwrite? (y/N)
User responded: n
```

### Example 2: Continue Prompt

**Terminal Prompt**:
```
Continue with operation? (Y/n)
```

**GUI Dialog**:
```
┌─────────────────────────────────────────┐
│        User Input Required               │
├─────────────────────────────────────────┤
│                                          │
│  Continue with operation? (Y/n)         │
│                                          │
├─────────────────────────────────────────┤
│              [ Yes ]  [ No ]             │
│              ^^^^^                       │
│            (default)                     │
└─────────────────────────────────────────┘
```

## Technical Details

### Default Value Detection

The system intelligently detects default values:

```python
def extract_default(prompt_line):
    if "(Y/n)" in prompt_line:
        return "y"  # Yes is default (capitalized)
    elif "(y/N)" in prompt_line:
        return "n"  # No is default (capitalized)
    elif "[Y/n]" in prompt_line:
        return "y"
    elif "[y/N]" in prompt_line:
        return "n"
    else:
        return ""  # No default
```

### Thread Safety

All GUI operations are performed on the main Qt thread:

```python
# In background thread:
self.interactive_prompt_signal.emit(prompt_text, default_value)

# Wait for response
while self.waiting_for_response:
    time.sleep(0.1)

return self.interactive_response

# In main thread (via signal):
def _request_interactive_response_safe(self, prompt, default):
    # Show dialog
    reply = QMessageBox.question(...)
    # Store response
    self.interactive_response = "y\n" if reply == Yes else "n\n"
    self.waiting_for_response = False
```

### Response Format

Responses are formatted correctly for terminal input:
- Lowercase letter: `"y\n"` or `"n\n"`
- Includes newline: Simulates pressing Enter
- Flushed immediately: `process.stdin.flush()`

## Prevention Strategies Used

### wget Commands

**Before**:
```bash
sudo wget -NP /etc/apt/sources.list.d/ <URL>
# -N flag causes prompts if file exists
```

**After**:
```bash
sudo rm -f /etc/apt/sources.list.d/winehq-*.sources
sudo wget -P /etc/apt/sources.list.d/ <URL>
# Remove first, no overwrite prompt possible
```

### Environment Variables

Set for all commands:
```python
env['DEBIAN_FRONTEND'] = 'noninteractive'  # No Debian prompts
env['NEEDRESTART_MODE'] = 'a'              # Auto-restart services
env['APT_LISTCHANGES_FRONTEND'] = 'none'   # Skip change lists
```

### Command Flags

- **apt**: `-y` (assume yes)
- **dnf**: `-y` (assume yes)
- **pacman**: `--noconfirm` (no confirmations)
- **zypper**: `-y` (assume yes)
- **winetricks**: `--unattended` (no interactive mode)

## Benefits

### For Users
1. **Never stuck**: No hidden prompts causing hangs
2. **Clear context**: See exactly what's being asked
3. **Visual feedback**: Professional dialog boxes
4. **Smart defaults**: Recommended choices pre-selected
5. **Logged actions**: All prompts and responses logged

### For Developers
1. **Robust**: Handles unexpected prompts gracefully
2. **Maintainable**: Easy to add new prompt patterns
3. **Debuggable**: All prompts logged for troubleshooting
4. **Extensible**: Can add custom handling for specific prompts

## Known Limitations

### Not Detected (By Design)
These are intentionally NOT intercepted:
1. **Application installers**: When running `.exe` files (Affinity installers)
   - Users need to see and interact with actual installer GUIs
   - License agreements, install paths, etc.

2. **Password prompts**: Handled by dedicated sudo password system
   - More secure than generic prompt handling
   - Session-based caching

### Platform Specific
- Uses `select.select()` which is Unix/Linux specific
- Fallback behavior on systems without `select` (just waits)

## Testing

### How to Test

1. **Create a test file**:
```bash
touch /tmp/test.txt
```

2. **Run command that would prompt**:
```python
success, stdout, stderr = self.run_command_interactive([
    "cp", "-i", "/tmp/test.txt", "/tmp/test2.txt"
])
```

3. **Expected behavior**:
   - If file exists, GUI dialog appears asking to overwrite
   - User's choice is respected
   - Operation completes without hanging

### Manual Testing Checklist
- [ ] File overwrite prompts (wget, cp, mv)
- [ ] Continue prompts (package managers)
- [ ] Replace prompts (configuration tools)
- [ ] Default value detection (Y/n vs y/N)
- [ ] Multiple prompts in sequence
- [ ] Cancel dialog (should send no/default)
- [ ] Timeout handling (30 second timeout)

## Future Enhancements

Potential improvements:
- [ ] Add more prompt patterns as discovered
- [ ] Remember user's choice for repeated prompts
- [ ] Add "Remember this choice" checkbox
- [ ] Support for more complex prompt formats
- [ ] Regex-based pattern matching for flexibility
- [ ] Option to always use safe defaults without asking

## Summary

The interactive prompt detection system ensures that **the AffinityLinuxInstaller never hangs on terminal prompts**. Through a combination of prevention (non-interactive flags) and detection (real-time monitoring), all user interaction is seamlessly moved to professional GUI dialogs.

This makes the application truly usable from any environment - application menus, desktop shortcuts, or automated scripts - with zero risk of invisible prompts causing problems.
