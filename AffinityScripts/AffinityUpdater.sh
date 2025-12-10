#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

################################################################################
# Distribution Detection
################################################################################

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        # Normalize "pika" to "pikaos" if detected
        if [ "$DISTRO" = "pika" ]; then
            DISTRO="pikaos"
        fi
    else
        echo -e "${RED}Error: Could not detect Linux distribution${NC}"
        exit 1
    fi
}

# Detect distribution
detect_distro

################################################################################
# Distribution Warnings
################################################################################

# Check for unsupported distributions
case $DISTRO in
    "ubuntu"|"linuxmint"|"zorin"|"bazzite")
        echo ""
        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}${BOLD}                    ⚠️   WARNING: UNSUPPORTED DISTRIBUTION   ⚠️${NC}"
        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${RED}${BOLD}YOU ARE ON YOUR OWN!${NC}"
        echo ""
        echo -e "${YELLOW}${BOLD}The distribution you are using ($DISTRO) is OUT OF DATE and the script${NC}"
        echo -e "${YELLOW}${BOLD}will NOT be built around it.${NC}"
        echo ""
        echo -e "${CYAN}${BOLD}For a modern, stable Linux experience with proper support, please consider${NC}"
        echo -e "${CYAN}${BOLD}switching to one of these recommended distributions:${NC}"
        echo ""
        echo -e "${GREEN}  • PikaOS 4${NC}"
        echo -e "${GREEN}  • CachyOS${NC}"
        echo -e "${GREEN}  • Nobara${NC}"
        echo ""
        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}Continuing anyway (no support will be provided)...${NC}"
        echo ""
        sleep 2
        ;;
    "pikaos")
        echo ""
        echo -e "${YELLOW}${BOLD}⚠️  PikaOS Special Notice${NC}"
        echo ""
        echo -e "${CYAN}PikaOS's built-in Wine has compatibility issues with Affinity applications.${NC}"
        echo -e "${CYAN}If you haven't already, please replace it with WineHQ staging from Debian.${NC}"
        echo ""
        echo -e "${BOLD}If needed, run these commands to set up WineHQ staging:${NC}"
        echo ""
        echo -e "${GREEN}sudo mkdir -pm755 /etc/apt/keyrings${NC}"
        echo -e "${GREEN}wget -O - https://dl.winehq.org/wine-builds/winehq.key | sudo gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key -${NC}"
        echo -e "${GREEN}sudo dpkg --add-architecture i386${NC}"
        echo -e "${GREEN}sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/forky/winehq-forky.sources${NC}"
        echo -e "${GREEN}sudo apt update${NC}"
        echo -e "${GREEN}sudo apt install --install-recommends winehq-staging${NC}"
        echo ""
        sleep 2
        ;;
esac

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

# Function to update Affinity app
update_affinity() {
    local app_name=$1
    local directory="$HOME/.AffinityLinux"
    
    # Check if directory exists
    if [ ! -d "$directory" ]; then
        echo -e "${RED}Error: Affinity installation directory not found at $directory${NC}"
        echo -e "${YELLOW}Please run the installer script first (AffinityPhoto.sh, AffinityDesigner.sh, or AffinityPublisher.sh)${NC}"
        return 1
    fi
    
    # Check if Wine binary exists
    if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        echo -e "${RED}Error: Wine binary not found in $directory/ElementalWarriorWine/bin/wine${NC}"
        echo -e "${YELLOW}Please run the installer script first${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Please drag and drop the Affinity $app_name .exe installer into this terminal and press Enter:${NC}"
    read installer_path
    
    # Normalize the path
    installer_path=$(normalize_path "$installer_path")
    
    # Check if file exists and is readable
    if [ ! -f "$installer_path" ] || [ ! -r "$installer_path" ]; then
        echo -e "${RED}Invalid file path or file is not readable: $installer_path${NC}"
        return 1
    fi
    
    # Get the filename from the path and sanitize it (replace spaces)
    local filename=$(basename "$installer_path")
    # Replace spaces with dashes to avoid issues
    filename=$(echo "$filename" | tr ' ' '-')
    
    # Kill any running Wine processes before updating
    echo -e "${YELLOW}Stopping any running Wine processes...${NC}"
    wineserver -k 2>/dev/null || true
    
    # Copy installer to Affinity directory
    echo -e "${YELLOW}Copying installer...${NC}"
    cp "$installer_path" "$directory/$filename"
    
    # Run installer
    echo -e "${YELLOW}Running installer...${NC}"
    echo -e "${YELLOW}Click No if you get any errors. Press any key to continue.${NC}"
    read -n 1
    
    # Ensure Windows version is set to 11
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true
    
    # Run installer with debug messages suppressed
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    
    # Clean up installer files
    echo -e "${YELLOW}Cleaning up installer files...${NC}"
    rm -f "$directory/$filename"
    rm -f "$directory"/affinity*.exe
    
    echo -e "${GREEN}Affinity $app_name update completed!${NC}"
    
    # Offer to update desktop entry
    echo -e "${YELLOW}Would you like to update the desktop entry? (y/n):${NC}"
    read -n 1 -r desktop_update
    echo
    if [[ $desktop_update =~ ^[Yy]$ ]]; then
        update_all_in_one
    fi
}



# Function to install Affinity (runs the installer script)
install_affinity() {
    local script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
    local installer_script="$script_dir/AffinityLinuxInstaller.sh"
    
    if [ ! -f "$installer_script" ]; then
        echo -e "${RED}Error: Installer script not found at $installer_script${NC}"
        echo -e "${YELLOW}Please ensure AffinityLinuxInstaller.sh is in the same directory as this script${NC}"
        return 1
    fi
    
    # Make sure the installer script is executable
    chmod +x "$installer_script"
    
    echo -e "${YELLOW}Launching Affinity Installer...${NC}"
    echo -e "${YELLOW}Note: The installer will set up Wine and allow you to install or update Affinity applications${NC}"
    echo
    
    # Run the installer script
    bash "$installer_script"
}

# Main menu
show_menu() {
    echo -e "${GREEN}Affinity Updater${NC}"
    echo "1. Update Affinity Photo"
    echo "2. Update Affinity Designer"
    echo "3. Update Affinity Publisher"
    echo "4. Update Affinity"
    echo "5. Exit"
    echo -n "Please select an option (1-5): "
}

# Main script
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            update_affinity "Photo"
            ;;
        2)
            update_affinity "Designer"
            ;;
        3)
            update_affinity "Publisher"
            ;;
        4)
            install_affinity
            ;;
        5)
            echo -e "${GREEN}Thank you for using the Affinity Updater!${NC}"
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