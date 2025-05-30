#!/bin/bash

# Check if script is executable, if not make it executable
if [ ! -x "$0" ]; then
    echo "Making script executable..."
    chmod +x "$0"
fi

# Ensure script is being run with bash
if [ -z "$BASH_VERSION" ]; then
    echo "This script must be run with bash"
    exit 1
fi

# ==========================================
# Constants and Configuration
# ==========================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
        echo -e "${RED}Could not detect Linux distribution${NC}"
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
    
    if [ -n "$missing_deps" ]; then
        echo -e "${YELLOW}Missing dependencies: $missing_deps${NC}"
        install_dependencies
    else
        echo -e "${GREEN}All dependencies are installed!${NC}"
    fi
}

# Function to install dependencies based on distribution
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies for $DISTRO...${NC}"
    
    case $DISTRO in
        "ubuntu"|"linuxmint"|"pop")
            sudo apt update
            sudo apt install -y wine winetricks wget curl p7zip-full tar jq
            ;;
        "arch"|"cachyos")
            sudo pacman -S --needed wine winetricks wget curl p7zip tar jq
            ;;
        "fedora"|"nobara")
            sudo dnf install -y wine winetricks wget curl p7zip p7zip-plugins tar jq
            ;;
        "opensuse-tumbleweed"|"opensuse-leap")
            sudo zypper install -y wine winetricks wget curl p7zip tar jq
            ;;
        *)
            echo -e "${RED}Unsupported distribution: $DISTRO${NC}"
            echo "Please install the following packages manually:"
            echo "wine winetricks wget curl p7zip tar jq"
            exit 1
            ;;
    esac
}

# ==========================================
# Wine Setup Functions
# ==========================================

# Function to download and setup Wine
setup_wine() {
    local directory="$HOME/.AffinityLinux"
    local repo="Twig6943/ElementalWarrior-Wine-binaries"
    local filename="ElementalWarriorWine.zip"
    
    # Kill any running wine processes
    wineserver -k
    
    # Create install directory
    mkdir -p "$directory"
    
    # Fetch the latest release information from GitHub
    release_info=$(curl -s "https://api.github.com/repos/$repo/releases/latest")
    download_url=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .browser_download_url")
    
    if [ -z "$download_url" ]; then
        echo -e "${RED}File not found in the latest release${NC}"
        exit 1
    fi
    
    # Download the specific release asset
    wget -q "$download_url" -O "$directory/$filename"
    
    # Verify download
    github_size=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .size")
    local_size=$(wc -c < "$directory/$filename")
    
    if [ "$github_size" -ne "$local_size" ]; then
        echo -e "${RED}Download verification failed${NC}"
        echo "Please download $filename from $download_url and place it in $directory"
        read -n 1 -s -r -p "Press any key when ready..."
    fi
    
    # Extract wine binary
    unzip "$directory/$filename" -d "$directory"
    rm "$directory/$filename"
    
    # Download and setup additional files
    wget -q https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg -O "$HOME/.local/share/icons/AffinityPhoto.svg"
    wget -q https://archive.org/download/win-metadata/WinMetadata.zip -O "$directory/Winmetadata.zip"
    
    # Extract WinMetadata
    7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"
    rm "$directory/Winmetadata.zip"
    
    # Setup Wine
    WINEPREFIX="$directory" winetricks --unattended dotnet35 dotnet48 corefonts vcrun2022 allfonts
    WINEPREFIX="$directory" winetricks renderer=vulkan
    
    # Set Windows version to 11
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11
    
    # Apply dark theme
    wget -q https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg -O "$directory/wine-dark-theme.reg"
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
    rm "$directory/wine-dark-theme.reg"
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
    
    # Copy to desktop
    cp "$desktop_file" "$HOME/Desktop/Affinity$app_name.desktop"
}

# Function to install Affinity app
install_affinity() {
    local app_name=$1
    local directory="$HOME/.AffinityLinux"
    
    echo -e "${YELLOW}Please drag and drop the Affinity $app_name installer (.exe) into this terminal and press Enter:${NC}"
    read installer_path
    
    # Remove quotes if present
    installer_path=$(echo "$installer_path" | tr -d '"')
    
    if [ ! -f "$installer_path" ]; then
        echo -e "${RED}Invalid file path${NC}"
        return 1
    fi
    
    # Copy installer to Affinity directory
    cp "$installer_path" "$directory/"
    
    # Run installer
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory"/*.exe
    
    # Clean up installer
    rm "$directory"/*.exe
    
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
    esac
}

# ==========================================
# User Interface Functions
# ==========================================

# Main menu
show_menu() {
    echo -e "${GREEN}Affinity Installation Script${NC}"
    echo "1. Install Affinity Photo"
    echo "2. Install Affinity Designer"
    echo "3. Install Affinity Publisher"
    echo "4. Exit"
    echo -n "Please select an option (1-4): "
}

# ==========================================
# Main Script
# ==========================================

main() {
    # Detect distribution
    detect_distro
    echo -e "${GREEN}Detected distribution: $DISTRO $VERSION${NC}"
    
    # Check and install dependencies
    check_dependencies
    
    # Setup Wine (only once)
    setup_wine
    
    while true; do
        show_menu
        read -r choice
        
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
                echo -e "${GREEN}Thank you for using the Affinity Installation Script!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option${NC}"
                ;;
        esac
        
        echo
        read -n 1 -s -r -p "Press any key to continue..."
        clear
    done
}

# Run main function
main 