#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to download with progress bar
download_with_progress() {
    local url=$1
    local output=$2
    local description=$3
    
    echo "Downloading $description..."
    curl -L -# -C - --retry 3 --retry-delay 2 --retry-max-time 30 \
        -H "Accept: application/octet-stream" \
        -o "$output" "$url"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download $description"
        exit 1
    fi
}

# Function to install dependencies based on distribution
install_dependencies() {
    local distro=$1
    echo "Installing dependencies for $distro..."
    
    case $distro in
        "Arch Linux"|"CachyOS"|"EndeavourOS")
            if ! command_exists pacman; then
                echo "Error: pacman not found. Are you sure you're on an Arch-based distribution?"
                exit 1
            fi
            # Arch Linux packages
            sudo pacman -S --needed \
                wine \
                winetricks \
                wget \
                curl \
                p7zip \
                tar \
                jq \
                pv \
                wine-mono \
                wine-gecko \
                lib32-nvidia-utils \
                lib32-mesa \
                lib32-vulkan-icd-loader \
                vulkan-icd-loader
            ;;
        "Fedora"|"Nobara"|"Ultramarine")
            if ! command_exists dnf; then
                echo "Error: dnf not found. Are you sure you're on a Fedora-based distribution?"
                exit 1
            fi
            # Fedora packages
            sudo dnf install -y \
                wine \
                winetricks \
                wget \
                curl \
                p7zip \
                tar \
                jq \
                pv \
                wine-mono \
                wine-gecko \
                vulkan-loader \
                vulkan-loader.i686 \
                mesa-libGL \
                mesa-libGL.i686 \
                mesa-libEGL \
                mesa-libEGL.i686
            ;;
        "PikaOS")
            if ! command_exists apt; then
                echo "Error: apt not found. Are you sure you're on PikaOS?"
                exit 1
            fi
            sudo apt update
            sudo apt install -y \
                wine \
                winetricks \
                wget \
                curl \
                p7zip \
                tar \
                jq \
                pv \
                wine-mono \
                wine-gecko \
                libvulkan1 \
                libvulkan1:i386 \
                libgl1 \
                libgl1:i386
            ;;
        "Ubuntu"|"Linux Mint")
            if ! command_exists apt; then
                echo "Error: apt not found. Are you sure you're on Ubuntu or Linux Mint?"
                exit 1
            fi
            echo "WARNING: Ubuntu and Linux Mint have outdated dependencies in their repositories."
            echo "This may cause compatibility issues with Affinity applications."
            echo "It is recommended to use a more up-to-date distribution like Fedora, Nobara, or Arch Linux."
            read -p "Do you want to continue anyway? (y/N): " continue_choice
            if [[ ! $continue_choice =~ ^[Yy]$ ]]; then
                echo "Installation cancelled."
                exit 1
            fi
            sudo apt update
            sudo apt install -y \
                wine \
                winetricks \
                wget \
                curl \
                p7zip \
                tar \
                jq \
                pv \
                wine-mono \
                wine-gecko \
                libvulkan1 \
                libvulkan1:i386 \
                libgl1 \
                libgl1:i386
            ;;
        *)
            echo "Unsupported distribution: $distro"
            exit 1
            ;;
    esac
}

# Function to install Affinity application
install_affinity() {
    local app=$1
    local directory="$HOME/.AffinityLinux"
    local repo="Twig6943/ElementalWarrior-Wine-binaries"
    local filename="ElementalWarriorWine.zip"

    echo "Installing $app..."
    
    # Kill any running wine processes
    wineserver -k
    
    # Create install directory
    mkdir -p "$directory"

    # Download and verify Wine binary
    echo "Downloading Wine binary..."
    release_info=$(curl -s "https://api.github.com/repos/$repo/releases/latest")
    download_url=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .browser_download_url")
    [ -z "$download_url" ] && { echo "File not found in the latest release"; exit 1; }

    # Download Wine binary with progress
    download_with_progress "$download_url" "$directory/$filename" "Wine binary"

    # Verify download
    github_size=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .size")
    local_size=$(wc -c < "$directory/$filename")

    if [ "$github_size" -ne "$local_size" ]; then
        echo "File sizes do not match: GitHub size: $github_size bytes, Local size: $local_size bytes"
        echo "Download $filename from $download_url move to $directory and hit any button to continue"
        read -n 1
    fi

    # Set application-specific variables
    case $app in
        "Photo")
            icon_url="https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg"
            icon_name="AffinityPhoto.svg"
            app_name="Photo"
            app_path="Photo 2/Photo.exe"
            desktop_name="AffinityPhoto"
            comment="Professional photo editing software"
            startup_wm="photo.exe"
            ;;
        "Designer")
            icon_url="https://upload.wikimedia.org/wikipedia/commons/3/3c/Affinity_Designer_2-logo.svg"
            icon_name="AffinityDesigner.svg"
            app_name="Designer"
            app_path="Designer 2/Designer.exe"
            desktop_name="AffinityDesigner"
            comment="Professional vector graphics and design software"
            startup_wm="designer.exe"
            ;;
        "Publisher")
            icon_url="https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg"
            icon_name="AffinityPublisher.svg"
            app_name="Publisher"
            app_path="Publisher 2/Publisher.exe"
            desktop_name="AffinityPublisher"
            comment="Professional desktop publishing software"
            startup_wm="publisher.exe"
            ;;
    esac

    # Download application icon with progress
    download_with_progress "$icon_url" "/home/$USER/.local/share/icons/$icon_name" "Application icon"

    # Download WinMetadata with progress
    download_with_progress "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata"

    # Extract files
    echo "Extracting files..."
    echo "Extracting Wine binary..."
    unzip -p "$directory/$filename" | pv -s $(unzip -l "$directory/$filename" | tail -n 1 | awk '{print $1}') | unzip -q -d "$directory" -
    rm "$directory/$filename"
    
    echo "Extracting Windows metadata..."
    7z x -y "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" 2>&1 | pv -l -s $(7z l "$directory/Winmetadata.zip" | grep -c "^[0-9]") > /dev/null
    rm "$directory/Winmetadata.zip"

    # Configure Wine
    echo "Configuring Wine environment..."
    WINEPREFIX="$directory" winetricks --unattended dotnet35 dotnet48 corefonts vcrun2022 allfonts
    WINEPREFIX="$directory" winetricks renderer=vulkan

    # Prompt for installer
    echo "Download the Affinity $app_name .exe from https://store.serif.com/account/licences/"
    echo "Once downloaded place the .exe in $directory and press any key when ready."
    read -n 1

    echo "Click No if you get any errors. Press any key to continue."
    read -n 1

    # Set Windows version and run installer
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory"/*.exe
    rm "$directory"/affinity*.exe

    # Apply dark theme
    download_with_progress "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg" "$directory/wine-dark-theme.reg" "Dark theme"
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
    rm "$directory/wine-dark-theme.reg"

    # Remove old desktop entry if it exists
    rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"

    # Create new desktop entry
    cat > ~/.local/share/applications/$desktop_name.desktop << EOF
[Desktop Entry]
Name=Affinity $app_name
Comment=$comment
Icon=/home/$USER/.local/share/icons/$icon_name
Path=$directory
Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/$app_path\"
Terminal=false
NoDisplay=false
StartupWMClass=$startup_wm
Type=Application
Categories=Graphics;
StartupNotify=true
EOF

    # Copy desktop entry to desktop
    cp ~/.local/share/applications/$desktop_name.desktop ~/Desktop/$desktop_name.desktop

    echo "Installation of Affinity $app_name completed!"
}

# Function to update Affinity application
update_affinity() {
    local app=$1
    local directory="$HOME/.AffinityLinux"

    echo "Updating $app..."
    
    # Kill any running wine processes
    wineserver -k

    # Set application-specific variables
    case $app in
        "Photo")
            app_name="Photo"
            app_path="Photo 2/Photo.exe"
            desktop_name="AffinityPhoto"
            ;;
        "Designer")
            app_name="Designer"
            app_path="Designer 2/Designer.exe"
            desktop_name="AffinityDesigner"
            ;;
        "Publisher")
            app_name="Publisher"
            app_path="Publisher 2/Publisher.exe"
            desktop_name="AffinityPublisher"
            ;;
    esac

    # Check if installation exists
    if [ ! -d "$directory" ]; then
        echo "Error: Affinity installation not found at $directory"
        echo "Please install the application first."
        exit 1
    fi

    # Prompt for new installer
    echo "Download the new Affinity $app_name .exe from https://store.serif.com/account/licences/"
    echo "Once downloaded place the .exe in $directory and press any key when ready."
    read -n 1

    # Run the new installer
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory"/*.exe
    rm "$directory"/affinity*.exe

    echo "Update of Affinity $app_name completed!"
}

# Main menu
echo "Affinity Linux Installation Script"
echo "================================="
echo "Select operation:"
echo "1) Install new Affinity application"
echo "2) Update existing Affinity application"
read -p "Enter your choice (1-2): " operation_choice

case $operation_choice in
    1)
        echo "Select your distribution:"
        echo "1) Arch Linux"
        echo "2) CachyOS"
        echo "3) EndeavourOS"
        echo "4) Fedora"
        echo "5) Nobara"
        echo "6) Ultramarine"
        echo "7) PikaOS"
        echo "8) Ubuntu (Not Recommended)"
        echo "9) Linux Mint (Not Recommended)"
        read -p "Enter your choice (1-9): " distro_choice

        case $distro_choice in
            1) distro="Arch Linux" ;;
            2) distro="CachyOS" ;;
            3) distro="EndeavourOS" ;;
            4) distro="Fedora" ;;
            5) distro="Nobara" ;;
            6) distro="Ultramarine" ;;
            7) distro="PikaOS" ;;
            8) distro="Ubuntu" ;;
            9) distro="Linux Mint" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac

        echo "Select Affinity application to install:"
        echo "1) Affinity Photo"
        echo "2) Affinity Designer"
        echo "3) Affinity Publisher"
        read -p "Enter your choice (1-3): " app_choice

        case $app_choice in
            1) app="Photo" ;;
            2) app="Designer" ;;
            3) app="Publisher" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac

        # Install dependencies
        install_dependencies "$distro"

        # Install selected Affinity application
        install_affinity "$app"
        ;;
    2)
        echo "Select Affinity application to update:"
        echo "1) Affinity Photo"
        echo "2) Affinity Designer"
        echo "3) Affinity Publisher"
        read -p "Enter your choice (1-3): " app_choice

        case $app_choice in
            1) app="Photo" ;;
            2) app="Designer" ;;
            3) app="Publisher" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac

        # Update selected Affinity application
        update_affinity "$app"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Special Thanks section
echo "******************************"
echo "    Special Thanks"
echo "******************************"
echo "Ardishco (github.com/raidenovich)"
echo "Deviaze"
echo "Kemal"
echo "Jacazimbo <3"
echo "Kharoon"
echo "Jediclank134"
read -n 1 