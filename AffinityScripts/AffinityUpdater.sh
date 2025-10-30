#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    
    echo -e "${YELLOW}Please drag and drop the Affinity $app_name .exe installer into this terminal and press Enter:${NC}"
    read installer_path
    
    # Normalize the path
    installer_path=$(normalize_path "$installer_path")
    
    # Check if file exists and is readable
    if [ ! -f "$installer_path" ] || [ ! -r "$installer_path" ]; then
        echo -e "${RED}Invalid file path or file is not readable: $installer_path${NC}"
        return 1
    fi
    
    # Get the filename from the path
    local filename=$(basename "$installer_path")
    
    # Copy installer to Affinity directory
    echo -e "${YELLOW}Copying installer...${NC}"
    cp "$installer_path" "$directory/$filename"
    
    # Run installer
    echo -e "${YELLOW}Running installer...${NC}"
    echo -e "${YELLOW}Click No if you get any errors. Press any key to continue.${NC}"
    read -n 1
    
    # Run installer with debug messages suppressed
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    
    # Clean up installer
    rm "$directory/$filename"
    
    echo -e "${GREEN}Affinity $app_name update completed!${NC}"
}

# Function to create Affinity desktop entry
create_all_in_one_desktop_entry() {
    local icon_path=$1
    local desktop_file="$HOME/.local/share/applications/Affinity.desktop"
    local directory="$HOME/.AffinityLinux"
    
    echo "[Desktop Entry]" > "$desktop_file"
    echo "Name=Affinity" >> "$desktop_file"
    echo "Comment=Photo, Designer, Publisher and more" >> "$desktop_file"
    echo "Icon=$icon_path" >> "$desktop_file"
    echo "Path=$directory" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe\"" >> "$desktop_file"
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
    
    echo -e "${GREEN}Affinity desktop entry created/updated!${NC}"
}

# Function to update/create Affinity desktop entry
update_all_in_one() {
    local icon_path="$HOME/.local/share/icons/Affinity.png"
    
    # Check if icon exists, if not try to copy from script directory
    if [ ! -f "$icon_path" ]; then
        script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
        if [ -f "$script_dir/icons/Affinity.png" ]; then
            mkdir -p "$HOME/.local/share/icons"
            cp "$script_dir/icons/Affinity.png" "$icon_path"
            echo -e "${GREEN}Copied Affinity icon to icons folder${NC}"
        else
            echo -e "${YELLOW}Warning: Affinity.png not found, using Photo icon as fallback${NC}"
            icon_path="$HOME/.local/share/icons/AffinityPhoto.svg"
        fi
    fi
    
    create_all_in_one_desktop_entry "$icon_path"
}

# Main menu
show_menu() {
    echo -e "${GREEN}Affinity Updater${NC}"
    echo "1. Update Affinity Photo"
    echo "2. Update Affinity Designer"
    echo "3. Update Affinity Publisher"
    echo "4. Update/Create Affinity Desktop Entry"
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
            update_all_in_one
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