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
# Modern TUI Constants and Configuration
# ==========================================

# Modern color palette
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'
UNDERLINE='\033[4m'

# Primary colors (modern, vibrant)
BLUE='\033[38;5;39m'
CYAN='\033[38;5;51m'
GREEN='\033[38;5;46m'
YELLOW='\033[38;5;226m'
ORANGE='\033[38;5;208m'
RED='\033[38;5;196m'
MAGENTA='\033[38;5;201m'
PURPLE='\033[38;5;129m'

# Background colors
BG_DARK='\033[48;5;236m'
BG_LIGHT='\033[48;5;252m'

# Terminal size
TERM_WIDTH=$(tput cols 2>/dev/null || echo 80)
TERM_HEIGHT=$(tput lines 2>/dev/null || echo 24)

# Cursor control
CURSOR_SAVE='\033[s'
CURSOR_RESTORE='\033[u'
CURSOR_HIDE='\033[?25l'
CURSOR_SHOW='\033[?25h'
CLEAR_LINE='\033[2K'
CLEAR_TO_END='\033[0J'

# ==========================================
# Modern TUI Utility Functions
# ==========================================

# Clear screen and set up
init_screen() {
    clear
    stty -echo 2>/dev/null
    printf "$CURSOR_HIDE"
}

# Restore screen
restore_screen() {
    printf "$CURSOR_SHOW"
    stty echo 2>/dev/null
    clear
}

# Print with modern styling
print_header() {
    local text="$1"
    local color="${2:-$CYAN}"
    printf "${BOLD}${color}╔════════════════════════════════════════════════════════════════╗${RESET}\n"
    printf "${BOLD}${color}║${RESET} %-62s ${BOLD}${color}║${RESET}\n" "$text"
    printf "${BOLD}${color}╚════════════════════════════════════════════════════════════════╝${RESET}\n"
}

print_box() {
    local title="$1"
    local content="$2"
    local color="${3:-$CYAN}"
    
    printf "${BOLD}${color}╭─${RESET} ${BOLD}$title${RESET} ${BOLD}${color}─${RESET}"
    local line_len=${#title}
    local remaining=$((66 - line_len))
    printf "${BOLD}${color}%*s${RESET}\n" $remaining "" | tr ' ' '─'
    
    while IFS= read -r line; do
        printf "${color}│${RESET} %-64s ${color}│${RESET}\n" "$line"
    done <<< "$content"
    
    printf "${BOLD}${color}╰${RESET}%*s${BOLD}${color}╯${RESET}\n" 66 "" | tr ' ' '─'
}

print_success() {
    printf "${GREEN}✓${RESET} %s\n" "$1"
}

print_error() {
    printf "${RED}✗${RESET} %s\n" "$1"
}

print_info() {
    printf "${CYAN}ℹ${RESET} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}⚠${RESET} %s\n" "$1"
}

print_step() {
    local step="$1"
    local total="$2"
    local message="$3"
    printf "${BOLD}${BLUE}[$step/$total]${RESET} ${message}\n"
}

# Modern progress bar
show_progress() {
    local current=$1
    local total=$2
    local label="$3"
    local width=50
    
    local percent=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    # Build progress bar
    local bar=""
    for ((i=0; i<filled; i++)); do
        bar+="█"
    done
    for ((i=0; i<empty; i++)); do
        bar+="░"
    done
    
    printf "\r${CYAN}${label}${RESET} ${BLUE}[${GREEN}${bar}${BLUE}]${RESET} ${BOLD}${percent}%%${RESET}"
}

# Show animated spinner
show_spinner() {
    local pid=$1
    local message="$2"
    local spin='⣷⣯⣟⡿⢿⣻⣽⣾'
    local i=0
    
    printf "${CYAN}${message}${RESET} "
    while kill -0 $pid 2>/dev/null; do
        i=$(((i + 1) % 8))
        printf "\b${spin:$i:1}"
        sleep 0.1
    done
    printf "\b${GREEN}✓${RESET}\n"
}

# Modern menu selector
show_menu() {
    local title="$1"
    shift
    local options=("$@")
    local selected=0
    
    while true; do
        clear
        print_header "$title"
        echo ""
        
        for i in "${!options[@]}"; do
            if [ $i -eq $selected ]; then
                printf "${BOLD}${BG_LIGHT}${BLUE} ▶ ${options[i]}${RESET}\n"
            else
                printf "   ${options[i]}\n"
            fi
        done
        
        echo ""
        printf "${DIM}Use ↑↓ arrows to navigate, Enter to select, Q to quit${RESET}\n"
        
        # Read single character
        read -rsn1 key
        case "$key" in
            $'\033') # Escape sequence
                read -rsn2 key
                case "$key" in
                    '[A') # Up arrow
                        selected=$((selected - 1))
                        [ $selected -lt 0 ] && selected=$((${#options[@]} - 1))
                        ;;
                    '[B') # Down arrow
                        selected=$((selected + 1))
                        [ $selected -ge ${#options[@]} ] && selected=0
                        ;;
                esac
                ;;
            '') # Enter
                echo "${options[selected]}"
                return 0
                ;;
            'q'|'Q')
                echo "Exit"
                return 0
                ;;
        esac
    done
}

# Modern yes/no prompt
show_confirm() {
    local question="$1"
    local default="${2:-y}"
    
    while true; do
        printf "${BOLD}${YELLOW}?${RESET} ${question} ${DIM}[y/N]:${RESET} "
        read -r answer
        
        [ -z "$answer" ] && answer="$default"
        
        case "$answer" in
            [Yy]*)
                return 0
                ;;
            [Nn]*)
                return 1
                ;;
            *)
                printf "${RED}Please answer yes (y) or no (n)${RESET}\n"
                ;;
        esac
    done
}

# Modern input prompt
show_input() {
    local prompt="$1"
    local default="${2:-}"
    local result
    
    printf "${BOLD}${CYAN}→${RESET} ${prompt}"
    [ -n "$default" ] && printf " ${DIM}[$default]:${RESET} " || printf ": "
    read -r result
    
    [ -z "$result" ] && result="$default"
    echo "$result"
}

# Show status message
show_status() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "success")
            printf "${GREEN}✓${RESET} ${message}\n"
            ;;
        "error")
            printf "${RED}✗${RESET} ${message}\n"
            ;;
        "info")
            printf "${CYAN}ℹ${RESET} ${message}\n"
            ;;
        "warning")
            printf "${YELLOW}⚠${RESET} ${message}\n"
            ;;
        "progress")
            printf "${BLUE}⟳${RESET} ${message}\n"
            ;;
    esac
}

# ==========================================
# Utility Functions
# ==========================================

# Function to download files with progress
download_file() {
    local url=$1
    local output=$2
    local description=$3
    
    show_status "progress" "Downloading $description..."
    
    # Try curl first
    if command -v curl &> /dev/null; then
        if curl -# -L "$url" -o "$output" 2>&1; then
            show_status "success" "Downloaded $description"
            return 0
        fi
    fi
    
    # Fallback to wget
    if command -v wget &> /dev/null; then
        if wget --progress=bar:force:noscroll "$url" -O "$output" 2>&1; then
            show_status "success" "Downloaded $description"
            return 0
        fi
    fi
    
    show_status "error" "Failed to download $description"
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
        show_status "error" "Could not detect Linux distribution"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    for dep in wine winetricks wget curl 7z tar jq; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    # Check for zstd support
    if ! command -v unzstd &> /dev/null && ! command -v zstd &> /dev/null; then
        missing_deps+=("zstd")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        local deps_list=$(IFS=', '; echo "${missing_deps[*]}")
        print_box "Missing Dependencies" "The following packages are required:\n\n${deps_list}\n\nThey will be installed automatically." "$ORANGE"
        
        if show_confirm "Install missing dependencies?" "y"; then
            install_dependencies
        else
            show_status "error" "Cannot continue without required dependencies"
            exit 1
        fi
    else
        show_status "success" "All dependencies are installed"
    fi
}

# Function to install dependencies based on distribution
install_dependencies() {
    show_status "progress" "Installing dependencies for $DISTRO..."
    
    case $DISTRO in
        "ubuntu"|"linuxmint"|"pop"|"pikaos")
            sudo apt update && sudo apt install -y wine winetricks wget curl p7zip-full tar jq zstd
            ;;
        "arch"|"cachyos")
            sudo pacman -S --needed wine winetricks wget curl p7zip tar jq zstd
            ;;
        "fedora"|"nobara")
            sudo dnf install -y wine winetricks wget curl p7zip p7zip-plugins tar jq zstd
            ;;
        "opensuse-tumbleweed"|"opensuse-leap")
            sudo zypper install -y wine winetricks wget curl p7zip tar jq zstd
            ;;
        *)
            print_box "Unsupported Distribution" "Your distribution ($DISTRO) is not directly supported.\n\nPlease install these packages manually:\nwine winetricks wget curl p7zip tar jq zstd" "$RED"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        show_status "success" "Dependencies installed successfully"
    else
        show_status "error" "Failed to install dependencies"
        exit 1
    fi
}

# ==========================================
# Wine Setup Functions
# ==========================================

# Function to verify Windows version
verify_windows_version() {
    local directory="$HOME/.AffinityLinux"
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
        print_box "Wine Already Installed" "Wine appears to be already set up.\n\nDo you want to reinstall it?" "$YELLOW"
        if ! show_confirm "Reinstall Wine?" "n"; then
            show_status "info" "Using existing Wine installation"
            return 0
        fi
        show_status "progress" "Removing existing Wine installation..."
        wineserver -k 2>/dev/null || true
        rm -rf "$directory"
    fi
    
    wineserver -k 2>/dev/null || true
    mkdir -p "$directory"
    
    # Download Wine
    print_step 1 7 "Downloading Wine binaries"
    if ! download_file "$wine_url" "$directory/$filename" "Wine binaries"; then
        show_status "error" "Failed to download Wine binaries"
        return 1
    fi
    
    # Extract Wine
    print_step 2 7 "Extracting Wine binaries"
    show_status "progress" "Extracting..."
    tar -xzf "$directory/$filename" -C "$directory" 2>/dev/null
    rm "$directory/$filename"
    
    # Find and link Wine directory
    wine_dir=$(find "$directory" -name "ElementalWarriorWine*" -type d | head -1)
    if [ -n "$wine_dir" ] && [ "$wine_dir" != "$directory/ElementalWarriorWine" ]; then
        ln -sf "$wine_dir" "$directory/ElementalWarriorWine"
    fi
    
    if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        show_status "error" "Wine binary not found after extraction"
        exit 1
    fi
    
    # Setup icons
    print_step 3 7 "Downloading application icons"
    mkdir -p "$HOME/.local/share/icons"
    download_file "https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg" "$HOME/.local/share/icons/AffinityPhoto.svg" "Affinity Photo icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/8/8a/Affinity_Designer_V2_icon.svg" "$HOME/.local/share/icons/AffinityDesigner.svg" "Affinity Designer icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg" "$HOME/.local/share/icons/AffinityPublisher.svg" "Affinity Publisher icon" || true
    
    script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
    if [ -f "$script_dir/icons/Affinity.png" ]; then
        cp "$script_dir/icons/Affinity.png" "$HOME/.local/share/icons/Affinity.png"
    fi
    
    # Download WinMetadata
    print_step 4 7 "Downloading Windows metadata"
    download_file "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata" || true
    
    mkdir -p "$directory/drive_c/windows/system32"
    
    if [ -f "$directory/Winmetadata.zip" ]; then
        show_status "progress" "Extracting Windows metadata..."
        if command -v 7z &> /dev/null; then
            7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" -y >/dev/null 2>&1 || {
                if command -v unzip &> /dev/null; then
                    unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1 || true
                fi
            }
        elif command -v unzip &> /dev/null; then
            unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1
        fi
        rm -f "$directory/Winmetadata.zip"
    fi
    
    # Download vkd3d-proton
    print_step 5 7 "Downloading vkd3d-proton for OpenCL support"
    local vkd3d_url="https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst"
    local vkd3d_filename="vkd3d-proton-2.14.1.tar.zst"
    
    if ! download_file "$vkd3d_url" "$directory/$vkd3d_filename" "vkd3d-proton"; then
        show_status "warning" "Failed to download vkd3d-proton. OpenCL support may not work properly."
    else
        show_status "progress" "Extracting vkd3d-proton..."
        if command -v unzstd &> /dev/null; then
            unzstd -f "$directory/$vkd3d_filename" -o "$directory/vkd3d-proton.tar"
            tar -xf "$directory/vkd3d-proton.tar" -C "$directory"
            rm "$directory/vkd3d-proton.tar"
        elif command -v zstd &> /dev/null && tar --help 2>&1 | grep -q "use-compress-program"; then
            tar --use-compress-program=zstd -xf "$directory/$vkd3d_filename" -C "$directory"
        else
            show_status "error" "Cannot extract .tar.zst file. Please install zstd or unzstd."
            rm "$directory/$vkd3d_filename"
            return 1
        fi
        rm "$directory/$vkd3d_filename"
        
        local vkd3d_dir=$(find "$directory" -type d -name "vkd3d-proton-*" | head -1)
        if [ -n "$vkd3d_dir" ]; then
            local vkd3d_temp="$directory/vkd3d_dlls"
            mkdir -p "$vkd3d_temp"
            
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
            
            rm -rf "$vkd3d_dir"
        fi
    fi
    
    # Setup Wine environment
    print_step 6 7 "Configuring Wine environment"
    show_status "progress" "Installing .NET frameworks and fonts..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet35 dotnet48 corefonts vcrun2022 >/dev/null 2>&1
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout renderer=vulkan >/dev/null 2>&1
    
    verify_windows_version
    
    # Apply dark theme
    print_step 7 7 "Applying dark theme"
    download_file "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg" "$directory/wine-dark-theme.reg" "dark theme" || true
    if [ -f "$directory/wine-dark-theme.reg" ]; then
        WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg" >/dev/null 2>&1
        rm "$directory/wine-dark-theme.reg"
    fi
    
    echo ""
    show_status "success" "Wine setup completed successfully!"
    sleep 1
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
    
    path=$(echo "$path" | tr -d '"' | xargs)
    
    if [[ "$path" == file://* ]]; then
        path=$(echo "$path" | sed 's|^file://||')
        path=$(printf '%b' "${path//%/\\x}")
    fi
    
    if [[ ! "$path" = /* ]]; then
        path="$(pwd)/$path"
    fi
    
    path=$(realpath -q "$path" 2>/dev/null || echo "$path")
    
    echo "$path"
}

# Function to install Affinity app
install_affinity() {
    local app_name=$1
    local directory="$HOME/.AffinityLinux"
    
    local friendly_name=""
    case $app_name in
        "Photo") friendly_name="Affinity Photo" ;;
        "Designer") friendly_name="Affinity Designer" ;;
        "Publisher") friendly_name="Affinity Publisher" ;;
        "Add") friendly_name="Affinity Suite (v2)" ;;
    esac
    
    clear
    print_header "Install $friendly_name"
    echo ""
    
    local welcome_msg="Before we begin:\n\n"
    welcome_msg+="  1. Download the installer .exe file from:\n"
    welcome_msg+="     ${BOLD}https://store.serif.com/account/licences/${RESET}\n\n"
    welcome_msg+="  2. If you haven't downloaded it yet, you can cancel\n"
    welcome_msg+="     and return to the main menu.\n\n"
    welcome_msg+="Ready to proceed?"
    
    print_box "Welcome" "$welcome_msg" "$CYAN"
    echo ""
    
    if ! show_confirm "Proceed with installation?" "y"; then
        return 0
    fi
    
    verify_windows_version
    
    # Get installer path
    local installer_path=""
    while true; do
        clear
        print_header "Install $friendly_name"
        echo ""
        print_box "Select Installer" "Enter the full path to the installer .exe file\n\nYou can drag and drop the file into this terminal" "$BLUE"
        echo ""
        
        installer_path=$(show_input "Installer path")
        
        if [ -z "$installer_path" ]; then
            show_status "info" "Installation cancelled"
            return 0
        fi
        
        installer_path=$(normalize_path "$installer_path")
        
        if [ ! -f "$installer_path" ]; then
            print_box "File Not Found" "The file does not exist:\n\n$installer_path" "$RED"
            if ! show_confirm "Try again?" "y"; then
                return 0
            fi
            continue
        fi
        
        if [ ! -r "$installer_path" ]; then
            show_status "error" "The file is not readable: $installer_path"
            sleep 2
            continue
        fi
        
        if [[ ! "$installer_path" =~ \.(exe|EXE)$ ]]; then
            if ! show_confirm "The file doesn't appear to be a .exe file. Continue anyway?" "n"; then
                continue
            fi
        fi
        
        break
    done
    
    local filename=$(basename "$installer_path")
    
    clear
    print_header "Install $friendly_name"
    echo ""
    
    local confirm_msg="Ready to install:\n\n"
    confirm_msg+="  ${BOLD}Installer:${RESET} $filename\n"
    confirm_msg+="  ${BOLD}Path:${RESET} $installer_path\n\n"
    confirm_msg+="During installation:\n"
    confirm_msg+="  • Click 'No' if you see any error dialogs\n"
    confirm_msg+="  • Follow the installer prompts normally"
    
    print_box "Confirm Installation" "$confirm_msg" "$GREEN"
    echo ""
    
    if ! show_confirm "Proceed with installation?" "y"; then
        return 0
    fi
    
    show_status "progress" "Copying installer..."
    cp "$installer_path" "$directory/$filename"
    
    clear
    print_header "Install $friendly_name"
    echo ""
    print_box "Installing" "Launching $friendly_name installer...\n\nPlease follow the installer prompts.\nClick 'No' on any error dialogs." "$CYAN"
    echo ""
    
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    local install_status=$?
    
    rm -f "$directory/$filename"
    
    if [ $install_status -ne 0 ]; then
        if show_confirm "Did the installation complete successfully?" "y"; then
            show_status "info" "Proceeding with post-installation setup..."
        else
            show_status "error" "Installation cancelled"
            return 1
        fi
    fi
    
    # If installing Affinity (unified app), copy vkd3d-proton DLLs
    if [ "$app_name" = "Add" ]; then
        local affinity_dir="$directory/drive_c/Program Files/Affinity/Affinity"
        if [ -d "$affinity_dir" ]; then
            show_status "progress" "Installing vkd3d-proton DLLs for OpenCL support..."
            local vkd3d_temp="$directory/vkd3d_dlls"
            
            if [ -f "$vkd3d_temp/d3d12.dll" ]; then
                cp "$vkd3d_temp/d3d12.dll" "$affinity_dir/" 2>/dev/null || true
            fi
            if [ -f "$vkd3d_temp/d3d12core.dll" ]; then
                cp "$vkd3d_temp/d3d12core.dll" "$affinity_dir/" 2>/dev/null || true
            fi
            
            local reg_file="$directory/dll_overrides.reg"
            echo "REGEDIT4" > "$reg_file"
            echo "[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]" >> "$reg_file"
            echo "\"d3d12\"=\"native\"" >> "$reg_file"
            echo "\"d3d12core\"=\"native\"" >> "$reg_file"
            WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$reg_file" >/dev/null 2>&1 || true
            rm -f "$reg_file"
        fi
    fi
    
    rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"
    
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
    
    clear
    print_header "Installation Complete"
    echo ""
    print_box "Success" "$friendly_name has been installed successfully!\n\nYou can now launch it from your applications menu." "$GREEN"
    echo ""
    show_confirm "Press Enter to continue" >/dev/null
}

# ==========================================
# User Interface Functions
# ==========================================

# Function to show special thanks
show_special_thanks() {
    clear
    print_header "Special Thanks"
    echo ""
    
    local thanks="Contributors:\n\n"
    thanks+="  • Ardishco (github.com/raidenovich)\n"
    thanks+="  • Deviaze\n"
    thanks+="  • Kemal\n"
    thanks+="  • Jacazimbo <3\n"
    thanks+="  • Kharoon\n"
    thanks+="  • Jediclank134\n\n"
    thanks+="Thank you for your contributions!"
    
    print_box "Acknowledgments" "$thanks" "$PURPLE"
    echo ""
    show_confirm "Press Enter to continue" >/dev/null
}

# ==========================================
# Main Script
# ==========================================

main() {
    # Trap to restore screen on exit
    trap 'restore_screen; exit' INT TERM EXIT
    
    init_screen
    
    # Welcome screen
    clear
    print_header "Affinity Installation Script"
    echo ""
    
    detect_distro
    
    local welcome_msg="Welcome to the Affinity Installation Script!\n\n"
    welcome_msg+="This script will guide you through installing\n"
    welcome_msg+="Affinity applications on Linux using Wine.\n\n"
    welcome_msg+="${BOLD}Detected System:${RESET}\n"
    welcome_msg+="  Distribution: ${CYAN}$DISTRO $VERSION${RESET}"
    
    print_box "Welcome" "$welcome_msg" "$CYAN"
    echo ""
    
    if ! show_confirm "Continue with system checks?" "y"; then
        restore_screen
        exit 0
    fi
    
    check_dependencies
    
    clear
    print_header "Wine Setup"
    echo ""
    
    local wine_info="Wine needs to be set up before installing Affinity applications.\n\n"
    wine_info+="This includes:\n"
    wine_info+="  • Downloading Wine binaries\n"
    wine_info+="  • Installing required components\n"
    wine_info+="  • Configuring the environment\n\n"
    wine_info+="This may take several minutes."
    
    print_box "Wine Configuration" "$wine_info" "$YELLOW"
    echo ""
    
    if ! show_confirm "Proceed with Wine setup?" "y"; then
        show_status "error" "Wine must be configured before installing applications"
        restore_screen
        exit 0
    fi
    
    setup_wine
    
    # Main menu loop
    while true; do
        clear
        print_header "Main Menu"
        echo ""
        
        local choice=$(show_menu "Select an Application to Install" \
            "Install Affinity Photo" \
            "Install Affinity Designer" \
            "Install Affinity Publisher" \
            "Install Affinity Suite (v2)" \
            "Show Special Thanks" \
            "Exit")
        
        case "$choice" in
            "Install Affinity Photo")
                install_affinity "Photo"
                ;;
            "Install Affinity Designer")
                install_affinity "Designer"
                ;;
            "Install Affinity Publisher")
                install_affinity "Publisher"
                ;;
            "Install Affinity Suite (v2)")
                install_affinity "Add"
                ;;
            "Show Special Thanks")
                show_special_thanks
                ;;
            "Exit"|"")
                if show_confirm "Are you sure you want to exit?" "n"; then
                    restore_screen
                    print_header "Thank You"
                    echo ""
                    show_status "success" "Thank you for using the Affinity Installation Script!"
                    sleep 1
                    exit 0
                fi
                ;;
            *)
                show_status "warning" "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# Run main function
main
