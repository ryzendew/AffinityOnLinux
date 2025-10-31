#!/bin/bash

# Check if script is executable, if not make it executable
if [ ! -x "$(readlink -f "$0")" ]; then
    chmod +x "$(readlink -f "$0")"
fi

# Ensure script is being run with bash
if [ -z "$BASH_VERSION" ]; then
    echo "This script must be run with bash"
    exit 1
fi

# ==========================================
# Constants and Configuration
# ==========================================

# Colors for output (used when dialog is not available)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Dialog settings
DIALOG_HEIGHT=20
DIALOG_WIDTH=70
DIALOG_MENU_HEIGHT=10

# ==========================================
# TUI Utility Functions
# ==========================================

# Function to check if dialog is available
check_dialog() {
    if ! command -v dialog &> /dev/null; then
        return 1
    fi
    return 0
}

# Function to show message (with dialog if available)
show_msg() {
    local title="$1"
    local message="$2"
    
    if check_dialog; then
        dialog --title "$title" --msgbox "$message" $DIALOG_HEIGHT $DIALOG_WIDTH 2>&1 >/dev/tty
    else
        echo -e "${GREEN}$title${NC}"
        echo "$message"
        echo ""
        read -n 1 -s -r -p "Press any key to continue..."
    fi
}

# Function to show info box
show_info() {
    local title="$1"
    local message="$2"
    
    if check_dialog; then
        dialog --title "$title" --infobox "$message" 8 $DIALOG_WIDTH 2>&1 >/dev/tty
        sleep 2
    else
        echo -e "${YELLOW}$title: $message${NC}"
    fi
}

# Function to show yes/no dialog
show_yesno() {
    local title="$1"
    local message="$2"
    
    if check_dialog; then
        dialog --title "$title" --yesno "$message" $DIALOG_HEIGHT $DIALOG_WIDTH 2>&1 >/dev/tty
        return $?
    else
        echo -e "${YELLOW}$title${NC}"
        echo "$message"
        read -p "Continue? (y/n): " answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            return 0
        else
            return 1
        fi
    fi
}

# Function to show progress gauge (for file operations)
show_progress() {
    local percent="$1"
    local status="$2"
    
    if check_dialog; then
        echo "$percent" | dialog --title "Progress" --gauge "$status" 8 $DIALOG_WIDTH 0 2>&1 >/dev/tty
    else
        echo -e "${YELLOW}[$percent%] $status${NC}"
    fi
}

# Function to get file path using dialog
get_file_path() {
    local title="$1"
    local message="$2"
    local default_path="$3"
    
    if check_dialog; then
        local path=$(dialog --title "$title" \
            --inputbox "$message" $DIALOG_HEIGHT $DIALOG_WIDTH "$default_path" \
            2>&1 >/dev/tty)
        echo "$path"
    else
        echo -e "${YELLOW}$title${NC}"
        echo "$message"
        read -p "File path: " path
        echo "$path"
    fi
}

# ==========================================
# Utility Functions
# ==========================================

# Function to download files with progress bar
download_file() {
    local url=$1
    local output=$2
    local description=$3
    
    show_info "Downloading" "$description..."
    
    # Try curl first with progress bar
    if command -v curl &> /dev/null; then
        if check_dialog; then
            # Use dialog gauge for curl
            curl -L --progress-bar "$url" -o "$output" 2>&1 | \
                stdbuf -oL -eL tr '\r' '\n' | \
                stdbuf -oL -eL sed -u 's/^ *\([0-9]*\).*\([0-9]*\).*\([0-9]*%\).*/\1\n#Downloading: \2KB (\3)/' | \
                dialog --title "Download Progress" --gauge "$description" 8 $DIALOG_WIDTH 0 2>&1 >/dev/tty || \
                curl -# -L "$url" -o "$output"
        else
            curl -# -L "$url" -o "$output"
        fi
        if [ $? -eq 0 ]; then
            return 0
        fi
    fi
    
    # Fallback to wget if curl fails or isn't available
    if command -v wget &> /dev/null; then
        if check_dialog; then
            wget --progress=bar:force "$url" -O "$output" 2>&1 | \
                dialog --title "Download Progress" --gauge "$description" 8 $DIALOG_WIDTH 0 2>&1 >/dev/tty || \
                wget --progress=bar:force:noscroll "$url" -O "$output"
        else
            wget --progress=bar:force:noscroll "$url" -O "$output"
        fi
        if [ $? -eq 0 ]; then
            return 0
        fi
    fi
    
    show_msg "Error" "Failed to download $description"
    return 1
}

# ==========================================
# System Detection and Setup Functions
# ==========================================

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        show_msg "Error" "Could not detect Linux distribution"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    local missing_deps=""
    
    for dep in wine winetricks wget curl 7z tar jq; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+="$dep "
        fi
    done
    
    # Check for zstd support (needed for vkd3d-proton)
    if ! command -v unzstd &> /dev/null && ! command -v zstd &> /dev/null; then
        missing_deps+="zstd "
    fi
    
    # Check for dialog
    if ! command -v dialog &> /dev/null; then
        missing_deps+="dialog "
    fi
    
    if [ -n "$missing_deps" ]; then
        show_info "Missing Dependencies" "Missing: $missing_deps"
        if show_yesno "Install Dependencies" "Some dependencies are missing. Would you like to install them now?\n\nMissing: $missing_deps"; then
            install_dependencies
        else
            show_msg "Error" "Cannot continue without required dependencies."
            exit 1
        fi
    else
        show_info "Dependencies" "All dependencies are installed!"
    fi
}

# Function to install dependencies based on distribution
install_dependencies() {
    show_info "Installing Dependencies" "Installing dependencies for $DISTRO..."
    
    case $DISTRO in
        "ubuntu"|"linuxmint"|"pop"|"pikaos")
            sudo apt update
            sudo apt install -y wine winetricks wget curl p7zip-full tar jq zstd dialog
            ;;
        "arch"|"cachyos")
            sudo pacman -S --needed wine winetricks wget curl p7zip tar jq zstd dialog
            ;;
        "fedora"|"nobara")
            sudo dnf install -y wine winetricks wget curl p7zip p7zip-plugins tar jq zstd dialog
            ;;
        "opensuse-tumbleweed"|"opensuse-leap")
            sudo zypper install -y wine winetricks wget curl p7zip tar jq zstd dialog
            ;;
        *)
            show_msg "Error" "Unsupported distribution: $DISTRO\n\nPlease install the following packages manually:\nwine winetricks wget curl p7zip tar jq zstd dialog"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        show_msg "Success" "Dependencies installed successfully!"
    else
        show_msg "Error" "Failed to install dependencies. Please install them manually."
        exit 1
    fi
}

# ==========================================
# Wine Setup Functions
# ==========================================

# Function to verify Windows version
verify_windows_version() {
    local directory="$HOME/.AffinityLinux"
    # Try to set Windows version to 11, but ignore errors
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true
    return 0
}

# Function to download and setup Wine
setup_wine() {
    local directory="$HOME/.AffinityLinux"
    local wine_url="https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
    local filename="ElementalWarriorWine-x86_64.tar.gz"
    
    # Check if Wine is already set up
    if [ -d "$directory/ElementalWarriorWine" ] && [ -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        if show_yesno "Wine Already Installed" "Wine appears to be already set up.\n\nDo you want to reinstall it?"; then
            show_info "Cleaning Up" "Removing existing Wine installation..."
            wineserver -k 2>/dev/null || true
            rm -rf "$directory"
        else
            show_info "Skipping" "Using existing Wine installation."
            return 0
        fi
    fi
    
    # Kill any running wine processes
    wineserver -k 2>/dev/null || true
    
    # Create install directory
    mkdir -p "$directory"
    
    show_info "Downloading Wine" "Downloading ElementalWarriorWine..."
    # Download the specific Wine version
    if ! download_file "$wine_url" "$directory/$filename" "Wine binaries"; then
        show_msg "Error" "Failed to download Wine binaries"
        return 1
    fi
    
    # Extract wine binary
    show_info "Extracting" "Extracting Wine binaries..."
    tar -xzf "$directory/$filename" -C "$directory"
    rm "$directory/$filename"
    
    # Find the actual Wine directory and create a symlink if needed
    wine_dir=$(find "$directory" -name "ElementalWarriorWine*" -type d | head -1)
    if [ -n "$wine_dir" ] && [ "$wine_dir" != "$directory/ElementalWarriorWine" ]; then
        show_info "Linking" "Creating Wine directory symlink..."
        ln -sf "$wine_dir" "$directory/ElementalWarriorWine"
    fi
    
    # Verify Wine binary exists
    if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        show_msg "Error" "Wine binary not found after extraction.\n\nDirectory: $directory"
        exit 1
    fi
    
    # Create icons directory if it doesn't exist
    mkdir -p "$HOME/.local/share/icons"
    
    # Download and setup additional files
    show_info "Downloading Icons" "Downloading application icons..."
    download_file "https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg" "$HOME/.local/share/icons/AffinityPhoto.svg" "Affinity Photo icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/8/8a/Affinity_Designer_V2_icon.svg" "$HOME/.local/share/icons/AffinityDesigner.svg" "Affinity Designer icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg" "$HOME/.local/share/icons/AffinityPublisher.svg" "Affinity Publisher icon" || true
    
    # Copy Affinity icon from script directory to icons folder
    script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
    if [ -f "$script_dir/icons/Affinity.png" ]; then
        cp "$script_dir/icons/Affinity.png" "$HOME/.local/share/icons/Affinity.png"
    fi
    
    # Download WinMetadata
    show_info "Downloading" "Downloading Windows metadata..."
    download_file "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata" || true
    
    # Ensure the system32 directory exists before extraction
    mkdir -p "$directory/drive_c/windows/system32"
    
    # Extract WinMetadata
    show_info "Extracting" "Extracting Windows metadata..."
    if [ -f "$directory/Winmetadata.zip" ]; then
        if command -v 7z &> /dev/null; then
            7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" -y >/dev/null 2>&1
            if [ $? -ne 0 ]; then
                if command -v unzip &> /dev/null; then
                    unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1 || true
                fi
            fi
        elif command -v unzip &> /dev/null; then
            unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1
        fi
        rm -f "$directory/Winmetadata.zip"
    fi
    
    # Download and install vkd3d-proton for OpenCL support
    show_info "Downloading" "Downloading vkd3d-proton for OpenCL support..."
    local vkd3d_url="https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst"
    local vkd3d_filename="vkd3d-proton-2.14.1.tar.zst"
    
    if ! download_file "$vkd3d_url" "$directory/$vkd3d_filename" "vkd3d-proton"; then
        show_msg "Warning" "Failed to download vkd3d-proton. OpenCL support may not work properly."
    else
        # Extract vkd3d-proton
        show_info "Extracting" "Extracting vkd3d-proton..."
        if command -v unzstd &> /dev/null; then
            unzstd -f "$directory/$vkd3d_filename" -o "$directory/vkd3d-proton.tar"
            tar -xf "$directory/vkd3d-proton.tar" -C "$directory"
            rm "$directory/vkd3d-proton.tar"
        elif command -v zstd &> /dev/null && tar --help 2>&1 | grep -q "use-compress-program"; then
            tar --use-compress-program=zstd -xf "$directory/$vkd3d_filename" -C "$directory"
        else
            show_msg "Error" "Cannot extract .tar.zst file. Please install zstd or unzstd."
            rm "$directory/$vkd3d_filename"
            return 1
        fi
        rm "$directory/$vkd3d_filename"
        
        # Extract vkd3d-proton DLLs for later use
        local vkd3d_dir=$(find "$directory" -type d -name "vkd3d-proton-*" | head -1)
        if [ -n "$vkd3d_dir" ]; then
            local vkd3d_temp="$directory/vkd3d_dlls"
            mkdir -p "$vkd3d_temp"
            
            # Copy DLL files to temp location
            if [ -f "$vkd3d_dir/x64/d3d12.dll" ]; then
                cp "$vkd3d_dir/x64/d3d12.dll" "$vkd3d_temp/" 2>/dev/null || true
            elif [ -f "$vkd3d_dir/d3d12.dll" ]; then
                cp "$vkd3d_dir/d3d12.dll" "$vkd3d_temp/" 2>/dev/null || true
            fi
            
            if [ -f "$vkd3d_dir/x64/d3d12core.dll" ]; then
                cp "$vkd3d_dir/x64/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null || true
            elif [ -f "$vkd3d_dir/d3d12core.dll" ]; then
                cp "$vkd3d_dir/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null || true
            fi
            
            # Remove extracted vkd3d-proton directory
            rm -rf "$vkd3d_dir"
        fi
    fi
    
    # Setup Wine
    show_info "Configuring Wine" "Setting up Wine environment with required components..."
    if check_dialog; then
        WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet35 dotnet48 corefonts vcrun2022 2>&1 | \
            dialog --title "Wine Configuration" --progressbox "Installing .NET frameworks and fonts..." $DIALOG_HEIGHT $DIALOG_WIDTH 2>&1 >/dev/tty
        WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout renderer=vulkan 2>&1 | \
            dialog --title "Wine Configuration" --progressbox "Setting Vulkan renderer..." $DIALOG_HEIGHT $DIALOG_WIDTH 2>&1 >/dev/tty
    else
        WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet35 dotnet48 corefonts vcrun2022
        WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout renderer=vulkan
    fi
    
    # Set and verify Windows version to 11
    verify_windows_version
    
    # Apply dark theme
    show_info "Applying Theme" "Applying dark theme..."
    download_file "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg" "$directory/wine-dark-theme.reg" "dark theme" || true
    if [ -f "$directory/wine-dark-theme.reg" ]; then
        WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg" >/dev/null 2>&1
        rm "$directory/wine-dark-theme.reg"
    fi
    
    show_msg "Success" "Wine setup completed successfully!"
}

# ==========================================
# Affinity Installation Functions
# ==========================================

# Function to create desktop entry
create_desktop_entry() {
    local app_name=$1
    local app_path=$2
    local icon_path=$3
    local desktop_file="$HOME/.local/share/applications/Affinity$app_name.desktop"
    
    echo "[Desktop Entry]" > "$desktop_file"
    echo "Name=Affinity $app_name" >> "$desktop_file"
    echo "Comment=A powerful $app_name software." >> "$desktop_file"
    echo "Icon=$icon_path" >> "$desktop_file"
    echo "Path=$HOME/.AffinityLinux" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$HOME/.AffinityLinux $HOME/.AffinityLinux/ElementalWarriorWine/bin/wine \"$app_path\"" >> "$desktop_file"
    echo "Terminal=false" >> "$desktop_file"
    echo "NoDisplay=false" >> "$desktop_file"
    echo "StartupWMClass=${app_name,,}.exe" >> "$desktop_file"
    echo "Type=Application" >> "$desktop_file"
    echo "Categories=Graphics;" >> "$desktop_file"
    echo "StartupNotify=true" >> "$desktop_file"
}

# Function to create Affinity desktop entry
create_all_in_one_desktop_entry() {
    local icon_path=$1
    local desktop_file="$HOME/.local/share/applications/Affinity.desktop"
    local directory="$HOME/.AffinityLinux"
    
    echo "[Desktop Entry]" > "$desktop_file"
    echo "Name=Affinity Suite" >> "$desktop_file"
    echo "Comment=Photo, Designer, Publisher and more" >> "$desktop_file"
    echo "Icon=$icon_path" >> "$desktop_file"
    echo "Path=$directory" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Affinity/Affinity.exe\"" >> "$desktop_file"
    echo "Terminal=false" >> "$desktop_file"
    echo "NoDisplay=false" >> "$desktop_file"
    echo "Type=Application" >> "$desktop_file"
    echo "Categories=Graphics;" >> "$desktop_file"
    echo "StartupNotify=true" >> "$desktop_file"
    echo "StartupWMClass=affinity.exe" >> "$desktop_file"
    echo "Actions=Photo;Designer;Publisher;" >> "$desktop_file"
    echo "" >> "$desktop_file"
    echo "[Desktop Action Photo]" >> "$desktop_file"
    echo "Name=Affinity Photo" >> "$desktop_file"
    echo "Icon=$HOME/.local/share/icons/AffinityPhoto.svg" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe\"" >> "$desktop_file"
    echo "" >> "$desktop_file"
    echo "[Desktop Action Designer]" >> "$desktop_file"
    echo "Name=Affinity Designer" >> "$desktop_file"
    echo "Icon=$HOME/.local/share/icons/AffinityDesigner.svg" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Designer 2/Designer.exe\"" >> "$desktop_file"
    echo "" >> "$desktop_file"
    echo "[Desktop Action Publisher]" >> "$desktop_file"
    echo "Name=Affinity Publisher" >> "$desktop_file"
    echo "Icon=$HOME/.local/share/icons/AffinityPublisher.svg" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe\"" >> "$desktop_file"
}

# Function to normalize and validate file path
normalize_path() {
    local path="$1"
    
    # Remove quotes and trim whitespace
    path=$(echo "$path" | tr -d '"' | xargs)
    
    # Handle file:// URLs (common when dragging from file managers)
    if [[ "$path" == file://* ]]; then
        path=$(echo "$path" | sed 's|^file://||')
        # URL decode the path
        path=$(printf '%b' "${path//%/\\x}")
    fi
    
    # Convert to absolute path if relative
    if [[ ! "$path" = /* ]]; then
        path="$(pwd)/$path"
    fi
    
    # Normalize path (remove . and .. components)
    path=$(realpath -q "$path" 2>/dev/null || echo "$path")
    
    echo "$path"
}

# Function to install Affinity app
install_affinity() {
    local app_name=$1
    local directory="$HOME/.AffinityLinux"
    
    # Get friendly name
    local friendly_name=""
    case $app_name in
        "Photo") friendly_name="Affinity Photo" ;;
        "Designer") friendly_name="Affinity Designer" ;;
        "Publisher") friendly_name="Affinity Publisher" ;;
        "Add") friendly_name="Affinity Suite (v2)" ;;
    esac
    
    # Show welcome message
    local welcome_msg="Welcome to the $friendly_name installer!\n\n"
    welcome_msg+="Before we begin:\n\n"
    welcome_msg+="1. Make sure you have downloaded the installer .exe file\n"
    welcome_msg+="2. You can download it from:\n"
    welcome_msg+="   https://store.serif.com/account/licences/\n\n"
    welcome_msg+="3. If you haven't downloaded it yet, you can cancel and\n"
    welcome_msg+="   return to the main menu.\n\n"
    welcome_msg+="Ready to proceed?"
    
    if ! show_yesno "Install $friendly_name" "$welcome_msg"; then
        return 0
    fi
    
    # Verify Windows version before installation
    verify_windows_version
    
    # Get installer path
    local installer_path=""
    while true; do
        installer_path=$(get_file_path "Select Installer" \
            "Please enter the full path to the $friendly_name installer .exe file:\n\nYou can drag and drop the file into this terminal.\n\n(Leave empty to cancel)" \
            "")
        
        if [ -z "$installer_path" ]; then
            show_info "Cancelled" "Installation cancelled by user."
            return 0
        fi
        
        # Normalize the path
        installer_path=$(normalize_path "$installer_path")
        
        # Check if file exists and is readable
        if [ ! -f "$installer_path" ]; then
            if ! show_yesno "File Not Found" "The file does not exist:\n\n$installer_path\n\nWould you like to try again?"; then
                return 0
            fi
            continue
        fi
        
        if [ ! -r "$installer_path" ]; then
            show_msg "Error" "The file is not readable:\n\n$installer_path\n\nPlease check file permissions."
            return 1
        fi
        
        # Check if it looks like an exe file
        if [[ ! "$installer_path" =~ \.(exe|EXE)$ ]]; then
            if ! show_yesno "Warning" "The file doesn't appear to be a .exe file:\n\n$installer_path\n\nContinue anyway?"; then
                continue
            fi
        fi
        
        break
    done
    
    # Get the filename from the path
    local filename=$(basename "$installer_path")
    
    # Confirm installation
    local confirm_msg="Ready to install $friendly_name\n\n"
    confirm_msg+="Installer: $filename\n"
    confirm_msg+="Path: $installer_path\n\n"
    confirm_msg+="During installation:\n"
    confirm_msg+="- Click 'No' if you see any error dialogs\n"
    confirm_msg+="- Follow the installer prompts normally\n\n"
    confirm_msg+="Proceed with installation?"
    
    if ! show_yesno "Confirm Installation" "$confirm_msg"; then
        return 0
    fi
    
    # Copy installer to Affinity directory
    show_info "Preparing" "Copying installer..."
    cp "$installer_path" "$directory/$filename"
    
    # Run installer
    show_info "Installing" "Launching $friendly_name installer...\n\nPlease follow the installer prompts.\nClick 'No' on any error dialogs."
    
    # Temporarily disable dialog to show installer window properly
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    local install_status=$?
    
    # Clean up installer
    rm -f "$directory/$filename"
    
    # Check installation status
    if [ $install_status -ne 0 ]; then
        if show_yesno "Installation Issue" "The installer may have encountered an issue.\n\nDid the installation complete successfully?"; then
            show_info "Continuing" "Proceeding with post-installation setup..."
        else
            show_msg "Error" "Installation cancelled. Please try again."
            return 1
        fi
    fi
    
    # If installing Affinity (unified app), copy vkd3d-proton DLLs and add to Wine libraries
    if [ "$app_name" = "Add" ]; then
        local affinity_dir="$directory/drive_c/Program Files/Affinity/Affinity"
        if [ -d "$affinity_dir" ]; then
            show_info "Configuring" "Installing vkd3d-proton DLLs for OpenCL support..."
            local vkd3d_temp="$directory/vkd3d_dlls"
            
            # Copy DLLs to Affinity directory
            if [ -f "$vkd3d_temp/d3d12.dll" ]; then
                cp "$vkd3d_temp/d3d12.dll" "$affinity_dir/" 2>/dev/null || true
            fi
            if [ -f "$vkd3d_temp/d3d12core.dll" ]; then
                cp "$vkd3d_temp/d3d12core.dll" "$affinity_dir/" 2>/dev/null || true
            fi
            
            # Add DLLs to Wine's library overrides using regedit
            local reg_file="$directory/dll_overrides.reg"
            echo "REGEDIT4" > "$reg_file"
            echo "[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]" >> "$reg_file"
            echo "\"d3d12\"=\"native\"" >> "$reg_file"
            echo "\"d3d12core\"=\"native\"" >> "$reg_file"
            WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$reg_file" >/dev/null 2>&1 || true
            rm -f "$reg_file"
        fi
    fi
    
    # Remove Wine's default desktop entry
    rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"
    
    # Create desktop entry
    case $app_name in
        "Photo")
            create_desktop_entry "Photo" "$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe" "$HOME/.local/share/icons/AffinityPhoto.svg"
            ;;
        "Designer")
            create_desktop_entry "Designer" "$directory/drive_c/Program Files/Affinity/Designer 2/Designer.exe" "$HOME/.local/share/icons/AffinityDesigner.svg"
            ;;
        "Publisher")
            create_desktop_entry "Publisher" "$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe" "$HOME/.local/share/icons/AffinityPublisher.svg"
            ;;
        "Add")
            # Create Affinity desktop entry
            icon_path="$HOME/.local/share/icons/Affinity.png"
            if [ ! -f "$icon_path" ]; then
                script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
                if [ -f "$script_dir/icons/Affinity.png" ]; then
                    cp "$script_dir/icons/Affinity.png" "$icon_path"
                else
                    icon_path="$HOME/.local/share/icons/AffinityPhoto.svg"
                fi
            fi
            create_all_in_one_desktop_entry "$icon_path"
            ;;
    esac
    
    show_msg "Success" "$friendly_name has been installed successfully!\n\nYou can now launch it from your applications menu."
}

# ==========================================
# User Interface Functions
# ==========================================

# Function to show special thanks
show_special_thanks() {
    local thanks="Special Thanks to:\n\n"
    thanks+="• Ardishco (github.com/raidenovich)\n"
    thanks+="• Deviaze\n"
    thanks+="• Kemal\n"
    thanks+="• Jacazimbo <3\n"
    thanks+="• Kharoon\n"
    thanks+="• Jediclank134\n\n"
    thanks+="Thank you for your contributions!"
    
    show_msg "Special Thanks" "$thanks"
}

# Function to show main menu using dialog
show_menu() {
    if check_dialog; then
        dialog --title "Affinity Installation Script" \
            --menu "Welcome to the Affinity Installation Script!\n\nSelect an option:" \
            $DIALOG_HEIGHT $DIALOG_WIDTH $DIALOG_MENU_HEIGHT \
            "1" "Install Affinity Photo" \
            "2" "Install Affinity Designer" \
            "3" "Install Affinity Publisher" \
            "4" "Install Affinity Suite (v2)" \
            "5" "Show Special Thanks" \
            "6" "Exit" \
            2>&1 >/dev/tty
    else
        # Fallback menu
        echo -e "${GREEN}Affinity Installation Script${NC}"
        echo "1. Install Affinity Photo"
        echo "2. Install Affinity Designer"
        echo "3. Install Affinity Publisher"
        echo "4. Install Affinity Suite (v2)"
        echo "5. Show Special Thanks"
        echo "6. Exit"
        echo -n "Please select an option (1-6): "
        read choice
        echo "$choice"
    fi
}

# ==========================================
# Main Script
# ==========================================

main() {
    # Check terminal size
    if check_dialog; then
        # Ensure terminal is large enough
        local rows=$(tput lines)
        local cols=$(tput cols)
        if [ $rows -lt 20 ] || [ $cols -lt 70 ]; then
            show_msg "Warning" "Your terminal window is too small.\n\nPlease resize to at least 70x20 characters for the best experience."
        fi
    fi
    
    # Show welcome message
    local welcome="Welcome to the Affinity Installation Script!\n\n"
    welcome+="This script will guide you through installing\n"
    welcome+="Affinity applications on Linux using Wine.\n\n"
    welcome+="Detected System:\n"
    detect_distro
    welcome+="Distribution: $DISTRO $VERSION\n\n"
    welcome+="Press OK to continue with system checks..."
    
    show_msg "Welcome" "$welcome"
    
    # Check and install dependencies
    check_dependencies
    
    # Setup Wine (only once, unless user wants to reinstall)
    if ! show_yesno "Wine Setup" "Wine needs to be set up before installing Affinity applications.\n\nThis includes:\n• Downloading Wine binaries\n• Installing required components\n• Configuring the environment\n\nThis may take several minutes. Proceed?"; then
        show_msg "Cancelled" "Setup cancelled. Wine must be configured before installing applications."
        exit 0
    fi
    
    setup_wine
    
    # Main menu loop
    while true; do
        choice=$(show_menu)
        
        case $choice in
            1)
                install_affinity "Photo"
                ;;
            2)
                install_affinity "Designer"
                ;;
            3)
                install_affinity "Publisher"
                ;;
            4)
                install_affinity "Add"
                ;;
            5)
                show_special_thanks
                ;;
            6|"")
                if check_dialog; then
                    if show_yesno "Exit" "Are you sure you want to exit?"; then
                        show_msg "Thank You" "Thank you for using the Affinity Installation Script!"
                        clear
                        exit 0
                    fi
                else
                    echo -e "${GREEN}Thank you for using the Affinity Installation Script!${NC}"
                    exit 0
                fi
                ;;
            *)
                show_msg "Error" "Invalid option. Please try again."
                ;;
        esac
    done
}

# Run main function
main

