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
# GUI-Style TUI Constants
# ==========================================

# Colors
RESET='\033[0m'
BOLD='\033[1m'

# GUI-style colors
WINDOW_BG='\033[48;5;235m'
WINDOW_FG='\033[38;5;255m'
TITLE_BAR='\033[48;5;240m'
BUTTON_ACTIVE='\033[48;5;33m\033[38;5;255m'
BUTTON_INACTIVE='\033[48;5;238m\033[38;5;255m'
BUTTON_HOVER='\033[48;5;39m\033[38;5;255m'
SUCCESS='\033[38;5;46m'
ERROR='\033[38;5;196m'
WARNING='\033[38;5;226m'
INFO='\033[38;5;51m'
ACCENT='\033[38;5;201m'

# Terminal control
CURSOR_HIDE='\033[?25l'
CURSOR_SHOW='\033[?25h'
CLEAR_SCREEN='\033[2J'
CURSOR_HOME='\033[H'

# Terminal size
TERM_WIDTH=$(tput cols 2>/dev/null || echo 80)
TERM_HEIGHT=$(tput lines 2>/dev/null || echo 24)

# Window dimensions
WIN_WIDTH=70
WIN_HEIGHT=20
WIN_X=$(( (TERM_WIDTH - WIN_WIDTH) / 2 ))
WIN_Y=$(( (TERM_HEIGHT - WIN_HEIGHT) / 2 ))

# ==========================================
# GUI-Style Drawing Functions
# ==========================================

# Draw a window with title bar
draw_window() {
    local title="$1"
    local x="${2:-$WIN_X}"
    local y="${3:-$WIN_Y}"
    local width="${4:-$WIN_WIDTH}"
    local height="${5:-$WIN_HEIGHT}"
    
    # Move cursor to top-left
    printf "\033[%d;%dH" $y $x
    
    # Top border with title
    printf "${TITLE_BAR}${BOLD}"
    printf "╔"
    local title_len=${#title}
    local title_space=$((width - title_len - 4))
    printf " %s " "$title"
    printf "%*s" $title_space ""
    printf "╗${RESET}\n"
    
    # Window body
    for ((i=1; i<height-1; i++)); do
        printf "\033[%d;%dH" $((y + i)) $x
        printf "${WINDOW_BG}${WINDOW_FG}║"
        printf "%*s" $((width - 2)) ""
        printf "║${RESET}\n"
    done
    
    # Bottom border
    printf "\033[%d;%dH" $((y + height - 1)) $x
    printf "${WINDOW_BG}${WINDOW_FG}╚"
    for ((i=1; i<width-1; i++)); do
        printf "═"
    done
    printf "╝${RESET}\n"
}

# Draw text in window
draw_text() {
    local x=$1
    local y=$2
    local text="$3"
    local color="${4:-$WINDOW_FG}"
    
    printf "\033[%d;%dH" $y $x
    printf "${WINDOW_BG}${color}%s${RESET}" "$text"
}

# Draw button
draw_button() {
    local x=$1
    local y=$2
    local text="$3"
    local active="${4:-false}"
    
    local style=""
    if [ "$active" = "true" ]; then
        style="${BUTTON_HOVER}"
    else
        style="${BUTTON_INACTIVE}"
    fi
    
    local padding=$((14 - ${#text}))
    local left_pad=$((padding / 2))
    local right_pad=$((padding - left_pad))
    
    printf "\033[%d;%dH" $y $x
    printf "${style}"
    printf " %*s%s%*s " $left_pad "" "$text" $right_pad ""
    printf "${RESET}"
}

# Draw progress bar
draw_progress() {
    local x=$1
    local y=$2
    local width=$3
    local percent=$4
    local label="$5"
    
    local filled=$((width * percent / 100))
    local empty=$((width - filled))
    
    printf "\033[%d;%dH" $y $x
    printf "${WINDOW_BG}${WINDOW_FG}${label} "
    printf "${BUTTON_INACTIVE}"
    for ((i=0; i<filled; i++)); do
        printf "█"
    done
    for ((i=0; i<empty; i++)); do
        printf "░"
    done
    printf "${RESET}"
    printf "${WINDOW_BG}${WINDOW_FG} %3d%%${RESET}" $percent
}

# Clear window content area
clear_window_content() {
    local x=$1
    local y=$2
    local width=$3
    local height=$4
    
    for ((i=1; i<height-1; i++)); do
        printf "\033[%d;%dH" $((y + i)) $((x + 1))
        printf "${WINDOW_BG}${WINDOW_FG}%*s${RESET}" $((width - 2)) ""
    done
}

# Show message dialog
show_message() {
    local title="$1"
    local message="$2"
    local msg_width=60
    local msg_height=8
    local msg_x=$(( (TERM_WIDTH - msg_width) / 2 ))
    local msg_y=$(( (TERM_HEIGHT - msg_height) / 2 ))
    
    # Count lines in message
    local lines=$(echo "$message" | wc -l)
    msg_height=$((lines + 5))
    
    # Clear screen and draw
    printf "${CLEAR_SCREEN}${CURSOR_HOME}"
    
    draw_window "$title" $msg_x $msg_y $msg_width $msg_height
    
    # Draw message
    local y_offset=$((msg_y + 2))
    while IFS= read -r line; do
        draw_text $((msg_x + 2)) $y_offset "$line"
        ((y_offset++))
    done <<< "$message"
    
    # Draw OK button
    draw_button $((msg_x + msg_width/2 - 7)) $((msg_y + msg_height - 2)) "  OK  " true
    
    # Wait for input
    read -rsn1
}

# Show yes/no dialog
show_question() {
    local title="$1"
    local message="$2"
    local msg_width=60
    local msg_height=10
    local msg_x=$(( (TERM_WIDTH - msg_width) / 2 ))
    local msg_y=$(( (TERM_HEIGHT - msg_height) / 2 ))
    
    local lines=$(echo "$message" | wc -l)
    msg_height=$((lines + 7))
    
    local choice="yes"
    
    while true; do
        printf "${CLEAR_SCREEN}${CURSOR_HOME}"
        
        draw_window "$title" $msg_x $msg_y $msg_width $msg_height
        
        # Draw message
        local y_offset=$((msg_y + 2))
        while IFS= read -r line; do
            draw_text $((msg_x + 2)) $y_offset "$line"
            ((y_offset++))
        done <<< "$message"
        
        # Draw buttons
        draw_button $((msg_x + msg_width/2 - 18)) $((msg_y + msg_height - 2)) "  Yes  " $([ "$choice" = "yes" ] && echo "true" || echo "false")
        draw_button $((msg_x + msg_width/2 - 2)) $((msg_y + msg_height - 2)) "  No  " $([ "$choice" = "no" ] && echo "true" || echo "false")
        
        # Read input
        read -rsn1 key
        case "$key" in
            $'\033')
                read -rsn2 key
                case "$key" in
                    '[C') choice="no" ;;
                    '[D') choice="yes" ;;
                esac
                ;;
            '')
                [ "$choice" = "yes" ] && return 0 || return 1
                ;;
            'y'|'Y')
                return 0
                ;;
            'n'|'N')
                return 1
                ;;
        esac
    done
}

# Show input dialog
show_input() {
    local title="$1"
    local prompt="$2"
    local default="${3:-}"
    local input_width=60
    local input_height=8
    local input_x=$(( (TERM_WIDTH - input_width) / 2 ))
    local input_y=$(( (TERM_HEIGHT - input_height) / 2 ))
    
    printf "${CLEAR_SCREEN}${CURSOR_HOME}"
    
    draw_window "$title" $input_x $input_y $input_width $input_height
    
    draw_text $((input_x + 2)) $((input_y + 2)) "$prompt"
    
    # Draw input field
    printf "\033[%d;%dH" $((input_y + 4)) $((input_x + 2))
    printf "${WINDOW_BG}${BUTTON_INACTIVE}%*s${RESET}" $((input_width - 4)) ""
    
    # Get input
    printf "\033[%d;%dH" $((input_y + 4)) $((input_x + 3))
    printf "${WINDOW_BG}${WINDOW_FG}"
    read -r result
    printf "${RESET}"
    
    [ -z "$result" ] && result="$default"
    echo "$result"
}

# Show menu window
show_menu() {
    local title="$1"
    shift
    local options=("$@")
    local selected=0
    
    local menu_width=50
    local menu_height=$((${#options[@]} + 6))
    local menu_x=$(( (TERM_WIDTH - menu_width) / 2 ))
    local menu_y=$(( (TERM_HEIGHT - menu_height) / 2 ))
    
    while true; do
        printf "${CLEAR_SCREEN}${CURSOR_HOME}"
        
        draw_window "$title" $menu_x $menu_y $menu_width $menu_height
        
        # Draw options
        local y_offset=$((menu_y + 2))
        for i in "${!options[@]}"; do
            if [ $i -eq $selected ]; then
                draw_text $((menu_x + 2)) $y_offset "▶ ${options[i]}"
                printf "\033[%d;%dH" $y_offset $((menu_x + 1))
                printf "${BUTTON_HOVER}▶${RESET}"
            else
                draw_text $((menu_x + 2)) $y_offset "  ${options[i]}"
            fi
            ((y_offset++))
        done
        
        # Draw footer
        draw_text $((menu_x + 2)) $((menu_y + menu_height - 2)) "${INFO}↑↓${RESET} Navigate  ${INFO}Enter${RESET} Select  ${INFO}Q${RESET} Quit"
        
        # Read input
        read -rsn1 key
        case "$key" in
            $'\033')
                read -rsn2 key
                case "$key" in
                    '[A') # Up
                        selected=$((selected - 1))
                        [ $selected -lt 0 ] && selected=$((${#options[@]} - 1))
                        ;;
                    '[B') # Down
                        selected=$((selected + 1))
                        [ $selected -ge ${#options[@]} ] && selected=0
                        ;;
                esac
                ;;
            '')
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

# Show status window
show_status_window() {
    local title="$1"
    local status="$2"
    local message="$3"
    
    local status_width=50
    local status_height=6
    local status_x=$(( (TERM_WIDTH - status_width) / 2 ))
    local status_y=$(( (TERM_HEIGHT - status_height) / 2 ))
    
    printf "${CLEAR_SCREEN}${CURSOR_HOME}"
    
    draw_window "$title" $status_x $status_y $status_width $status_height
    
    local icon=""
    local color=""
    case "$status" in
        "success")
            icon="✓"
            color="$SUCCESS"
            ;;
        "error")
            icon="✗"
            color="$ERROR"
            ;;
        "warning")
            icon="⚠"
            color="$WARNING"
            ;;
        "info")
            icon="ℹ"
            color="$INFO"
            ;;
        "progress")
            icon="⟳"
            color="$INFO"
            ;;
    esac
    
    draw_text $((status_x + 2)) $((status_y + 2)) "${color}${icon}${RESET} ${WINDOW_FG}$message${RESET}"
    
    if [ "$status" != "progress" ]; then
        sleep 1.5
    fi
}

# Show progress window
show_progress_window() {
    local title="$1"
    local label="$2"
    local percent=$3
    
    local prog_width=50
    local prog_height=6
    local prog_x=$(( (TERM_WIDTH - prog_width) / 2 ))
    local prog_y=$(( (TERM_HEIGHT - prog_height) / 2 ))
    
    printf "${CLEAR_SCREEN}${CURSOR_HOME}"
    
    draw_window "$title" $prog_x $prog_y $prog_width $prog_height
    
    draw_progress $((prog_x + 2)) $((prog_y + 2)) 44 $percent "$label"
}

# ==========================================
# Utility Functions
# ==========================================

download_file() {
    local url=$1
    local output=$2
    local description=$3
    
    show_status_window "Downloading" "progress" "Downloading $description..."
    
    if command -v curl &> /dev/null; then
        if curl -# -L "$url" -o "$output" 2>&1; then
            show_status_window "Download Complete" "success" "Downloaded $description"
            return 0
        fi
    fi
    
    if command -v wget &> /dev/null; then
        if wget --progress=bar:force:noscroll "$url" -O "$output" 2>&1; then
            show_status_window "Download Complete" "success" "Downloaded $description"
            return 0
        fi
    fi
    
    show_status_window "Download Failed" "error" "Failed to download $description"
    return 1
}

# ==========================================
# System Detection
# ==========================================

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        show_status_window "Error" "error" "Could not detect Linux distribution"
        exit 1
    fi
}

check_dependencies() {
    local missing_deps=()
    
    for dep in wine winetricks wget curl 7z tar jq; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if ! command -v unzstd &> /dev/null && ! command -v zstd &> /dev/null; then
        missing_deps+=("zstd")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        local deps_list=$(IFS=', '; echo "${missing_deps[*]}")
        local msg="Missing dependencies:\n\n${deps_list}\n\nThey will be installed automatically."
        
        if show_question "Missing Dependencies" "$msg"; then
            install_dependencies
        else
            show_status_window "Error" "error" "Cannot continue without dependencies"
            exit 1
        fi
    else
        show_status_window "Dependencies" "success" "All dependencies installed"
    fi
}

install_dependencies() {
    show_status_window "Installing" "progress" "Installing dependencies for $DISTRO..."
    
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
            show_message "Error" "Unsupported distribution: $DISTRO\n\nPlease install:\nwine winetricks wget curl p7zip tar jq zstd"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        show_status_window "Success" "success" "Dependencies installed"
    else
        show_status_window "Error" "error" "Failed to install dependencies"
        exit 1
    fi
}

# ==========================================
# Wine Setup
# ==========================================

verify_windows_version() {
    local directory="$HOME/.AffinityLinux"
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true
}

setup_wine() {
    local directory="$HOME/.AffinityLinux"
    local wine_url="https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
    local filename="ElementalWarriorWine-x86_64.tar.gz"
    
    if [ -d "$directory/ElementalWarriorWine" ] && [ -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        if ! show_question "Wine Already Installed" "Wine is already set up.\n\nDo you want to reinstall it?"; then
            return 0
        fi
        wineserver -k 2>/dev/null || true
        rm -rf "$directory"
    fi
    
    wineserver -k 2>/dev/null || true
    mkdir -p "$directory"
    
    show_progress_window "Wine Setup" "Downloading Wine" 10
    download_file "$wine_url" "$directory/$filename" "Wine binaries" || return 1
    
    show_progress_window "Wine Setup" "Extracting Wine" 30
    tar -xzf "$directory/$filename" -C "$directory" 2>/dev/null
    rm "$directory/$filename"
    
    wine_dir=$(find "$directory" -name "ElementalWarriorWine*" -type d | head -1)
    if [ -n "$wine_dir" ] && [ "$wine_dir" != "$directory/ElementalWarriorWine" ]; then
        ln -sf "$wine_dir" "$directory/ElementalWarriorWine"
    fi
    
    if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        show_status_window "Error" "error" "Wine binary not found"
        exit 1
    fi
    
    show_progress_window "Wine Setup" "Downloading Icons" 40
    mkdir -p "$HOME/.local/share/icons"
    download_file "https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg" "$HOME/.local/share/icons/AffinityPhoto.svg" "Icons" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/8/8a/Affinity_Designer_V2_icon.svg" "$HOME/.local/share/icons/AffinityDesigner.svg" "Icons" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg" "$HOME/.local/share/icons/AffinityPublisher.svg" "Icons" || true
    
    script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
    [ -f "$script_dir/icons/Affinity.png" ] && cp "$script_dir/icons/Affinity.png" "$HOME/.local/share/icons/Affinity.png"
    
    show_progress_window "Wine Setup" "Downloading Metadata" 50
    download_file "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata" || true
    
    mkdir -p "$directory/drive_c/windows/system32"
    if [ -f "$directory/Winmetadata.zip" ]; then
        if command -v 7z &> /dev/null; then
            7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" -y >/dev/null 2>&1 || {
                [ -f "$directory/Winmetadata.zip" ] && unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1 || true
            }
        elif command -v unzip &> /dev/null; then
            unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1
        fi
        rm -f "$directory/Winmetadata.zip"
    fi
    
    show_progress_window "Wine Setup" "Downloading vkd3d-proton" 60
    local vkd3d_url="https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst"
    local vkd3d_filename="vkd3d-proton-2.14.1.tar.zst"
    
    if download_file "$vkd3d_url" "$directory/$vkd3d_filename" "vkd3d-proton"; then
        if command -v unzstd &> /dev/null; then
            unzstd -f "$directory/$vkd3d_filename" -o "$directory/vkd3d-proton.tar"
            tar -xf "$directory/vkd3d-proton.tar" -C "$directory"
            rm "$directory/vkd3d-proton.tar"
        elif command -v zstd &> /dev/null && tar --help 2>&1 | grep -q "use-compress-program"; then
            tar --use-compress-program=zstd -xf "$directory/$vkd3d_filename" -C "$directory"
        fi
        rm "$directory/$vkd3d_filename"
        
        local vkd3d_dir=$(find "$directory" -type d -name "vkd3d-proton-*" | head -1)
        if [ -n "$vkd3d_dir" ]; then
            local vkd3d_temp="$directory/vkd3d_dlls"
            mkdir -p "$vkd3d_temp"
            [ -f "$vkd3d_dir/x64/d3d12.dll" ] && cp "$vkd3d_dir/x64/d3d12.dll" "$vkd3d_temp/" 2>/dev/null || \
            [ -f "$vkd3d_dir/d3d12.dll" ] && cp "$vkd3d_dir/d3d12.dll" "$vkd3d_temp/" 2>/dev/null || true
            [ -f "$vkd3d_dir/x64/d3d12core.dll" ] && cp "$vkd3d_dir/x64/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null || \
            [ -f "$vkd3d_dir/d3d12core.dll" ] && cp "$vkd3d_dir/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null || true
            rm -rf "$vkd3d_dir"
        fi
    fi
    
    show_progress_window "Wine Setup" "Configuring Wine" 80
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet35 dotnet48 corefonts vcrun2022 >/dev/null 2>&1
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout renderer=vulkan >/dev/null 2>&1
    verify_windows_version
    
    show_progress_window "Wine Setup" "Applying Theme" 90
    download_file "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg" "$directory/wine-dark-theme.reg" "dark theme" || true
    [ -f "$directory/wine-dark-theme.reg" ] && WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg" >/dev/null 2>&1 && rm "$directory/wine-dark-theme.reg"
    
    show_progress_window "Wine Setup" "Complete" 100
    sleep 0.5
    show_status_window "Success" "success" "Wine setup completed"
}

# ==========================================
# Desktop Entry Functions
# ==========================================

create_desktop_entry() {
    local app_name=$1
    local app_path=$2
    local icon_path=$3
    local desktop_file="$HOME/.local/share/applications/Affinity$app_name.desktop"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Affinity $app_name
Comment=A powerful $app_name software.
Icon=$icon_path
Path=$HOME/.AffinityLinux
Exec=env WINEPREFIX=$HOME/.AffinityLinux $HOME/.AffinityLinux/ElementalWarriorWine/bin/wine "$app_path"
Terminal=false
NoDisplay=false
StartupWMClass=${app_name,,}.exe
Type=Application
Categories=Graphics;
StartupNotify=true
EOF
}

create_all_in_one_desktop_entry() {
    local icon_path=$1
    local desktop_file="$HOME/.local/share/applications/Affinity.desktop"
    local directory="$HOME/.AffinityLinux"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Affinity Suite
Comment=Photo, Designer, Publisher and more
Icon=$icon_path
Path=$directory
Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine "$directory/drive_c/Program Files/Affinity/Affinity/Affinity.exe"
Terminal=false
NoDisplay=false
Type=Application
Categories=Graphics;
StartupNotify=true
StartupWMClass=affinity.exe
Actions=Photo;Designer;Publisher;

[Desktop Action Photo]
Name=Affinity Photo
Icon=$HOME/.local/share/icons/AffinityPhoto.svg
Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine "$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe"

[Desktop Action Designer]
Name=Affinity Designer
Icon=$HOME/.local/share/icons/AffinityDesigner.svg
Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine "$directory/drive_c/Program Files/Affinity/Designer 2/Designer.exe"

[Desktop Action Publisher]
Name=Affinity Publisher
Icon=$HOME/.local/share/icons/AffinityPublisher.svg
Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine "$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe"
EOF
}

normalize_path() {
    local path="$1"
    path=$(echo "$path" | tr -d '"' | xargs)
    if [[ "$path" == file://* ]]; then
        path=$(echo "$path" | sed 's|^file://||')
        path=$(printf '%b' "${path//%/\\x}")
    fi
    [[ ! "$path" = /* ]] && path="$(pwd)/$path"
    path=$(realpath -q "$path" 2>/dev/null || echo "$path")
    echo "$path"
}

# ==========================================
# Installation Function
# ==========================================

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
    
    local welcome_msg="Before we begin:\n\n"
    welcome_msg+="1. Download the installer .exe from:\n"
    welcome_msg+="   https://store.serif.com/account/licences/\n\n"
    welcome_msg+="2. If you haven't downloaded it yet, you can\n"
    welcome_msg+="   cancel and return to the main menu."
    
    if ! show_question "Install $friendly_name" "$welcome_msg"; then
        return 0
    fi
    
    verify_windows_version
    
    local installer_path=""
    while true; do
        installer_path=$(show_input "Select Installer" "Enter the full path to the installer .exe file\n(You can drag and drop the file)" "")
        
        [ -z "$installer_path" ] && return 0
        
        installer_path=$(normalize_path "$installer_path")
        
        if [ ! -f "$installer_path" ]; then
            if ! show_question "File Not Found" "The file does not exist:\n\n$installer_path\n\nTry again?"; then
                return 0
            fi
            continue
        fi
        
        [ ! -r "$installer_path" ] && show_status_window "Error" "error" "File is not readable" && continue
        
        [[ ! "$installer_path" =~ \.(exe|EXE)$ ]] && ! show_question "Warning" "The file doesn't appear to be a .exe file.\n\nContinue anyway?" && continue
        
        break
    done
    
    local filename=$(basename "$installer_path")
    local confirm_msg="Ready to install:\n\n"
    confirm_msg+="Installer: $filename\n"
    confirm_msg+="Path: $installer_path\n\n"
    confirm_msg+="During installation:\n"
    confirm_msg+="• Click 'No' if you see any error dialogs\n"
    confirm_msg+="• Follow the installer prompts normally"
    
    if ! show_question "Confirm Installation" "$confirm_msg"; then
        return 0
    fi
    
    show_status_window "Preparing" "progress" "Copying installer..."
    cp "$installer_path" "$directory/$filename"
    
    show_message "Installing" "Launching $friendly_name installer...\n\nPlease follow the installer prompts.\nClick 'No' on any error dialogs."
    
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    local install_status=$?
    
    rm -f "$directory/$filename"
    
    if [ $install_status -ne 0 ]; then
        if ! show_question "Installation" "Did the installation complete successfully?"; then
            show_status_window "Cancelled" "error" "Installation cancelled"
            return 1
        fi
    fi
    
    if [ "$app_name" = "Add" ]; then
        local affinity_dir="$directory/drive_c/Program Files/Affinity/Affinity"
        if [ -d "$affinity_dir" ]; then
            show_status_window "Configuring" "progress" "Installing vkd3d-proton DLLs..."
            local vkd3d_temp="$directory/vkd3d_dlls"
            [ -f "$vkd3d_temp/d3d12.dll" ] && cp "$vkd3d_temp/d3d12.dll" "$affinity_dir/" 2>/dev/null || true
            [ -f "$vkd3d_temp/d3d12core.dll" ] && cp "$vkd3d_temp/d3d12core.dll" "$affinity_dir/" 2>/dev/null || true
            
            local reg_file="$directory/dll_overrides.reg"
            cat > "$reg_file" << EOF
REGEDIT4
[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]
"d3d12"="native"
"d3d12core"="native"
EOF
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
            local icon_path="$HOME/.local/share/icons/Affinity.png"
            [ ! -f "$icon_path" ] && {
                script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
                [ -f "$script_dir/icons/Affinity.png" ] && cp "$script_dir/icons/Affinity.png" "$icon_path" || icon_path="$HOME/.local/share/icons/AffinityPhoto.svg"
            }
            create_all_in_one_desktop_entry "$icon_path"
            ;;
    esac
    
    show_status_window "Success" "success" "$friendly_name installed successfully!"
    sleep 1.5
}

# ==========================================
# Main Script
# ==========================================

main() {
    # Setup
    printf "${CURSOR_HIDE}"
    trap 'printf "${CURSOR_SHOW}"; clear; exit' INT TERM EXIT
    
    # Welcome
    detect_distro
    local welcome_msg="Welcome to the Affinity Installation Script!\n\n"
    welcome_msg+="This script will guide you through installing\n"
    welcome_msg+="Affinity applications on Linux using Wine.\n\n"
    welcome_msg+="Detected System:\n"
    welcome_msg+="Distribution: $DISTRO $VERSION"
    
    if ! show_question "Welcome" "$welcome_msg\n\nContinue with system checks?"; then
        printf "${CURSOR_SHOW}"
        clear
        exit 0
    fi
    
    check_dependencies
    
    local wine_info="Wine needs to be set up before installing\n"
    wine_info+="Affinity applications.\n\n"
    wine_info+="This includes:\n"
    wine_info+="• Downloading Wine binaries\n"
    wine_info+="• Installing required components\n"
    wine_info+="• Configuring the environment\n\n"
    wine_info+="This may take several minutes."
    
    if ! show_question "Wine Setup" "$wine_info\n\nProceed with Wine setup?"; then
        show_status_window "Error" "error" "Wine must be configured"
        printf "${CURSOR_SHOW}"
        clear
        exit 0
    fi
    
    setup_wine
    
    # Main menu loop
    while true; do
        local choice=$(show_menu "Main Menu" \
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
                local thanks="Contributors:\n\n"
                thanks+="• Ardishco (github.com/raidenovich)\n"
                thanks+="• Deviaze\n"
                thanks+="• Kemal\n"
                thanks+="• Jacazimbo <3\n"
                thanks+="• Kharoon\n"
                thanks+="• Jediclank134\n\n"
                thanks+="Thank you for your contributions!"
                show_message "Special Thanks" "$thanks"
                ;;
            "Exit"|"")
                if show_question "Exit" "Are you sure you want to exit?"; then
                    printf "${CURSOR_SHOW}"
                    clear
                    exit 0
                fi
                ;;
        esac
    done
}

# Run main function
main
