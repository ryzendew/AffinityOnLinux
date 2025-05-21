#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to download with progress bar and multi-threading
download_with_progress() {
    local url=$1
    local output=$2
    local description=$3
    
    echo "Downloading $description..."
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$output")"
    
    # Use aria2c for faster downloads with multiple connections
    aria2c --max-connection-per-server=16 \
           --min-split-size=1M \
           --max-concurrent-downloads=16 \
           --file-allocation=none \
           --continue=true \
           --retry-wait=2 \
           --max-tries=3 \
           --timeout=30 \
           --auto-file-renaming=false \
           --allow-overwrite=true \
           --summary-interval=1 \
           --human-readable=true \
           --show-console-readout=true \
           --console-log-level=notice \
           -d "$(dirname "$output")" \
           -o "$(basename "$output")" \
           "$url"
    
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
        "Arch Linux"|"EndeavourOS")
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
                aria2 \
                wine-mono \
                wine-gecko \
                lib32-nvidia-utils
            ;;
        "CachyOS")
            if ! command_exists pacman; then
                echo "Error: pacman not found. Are you sure you're on CachyOS?"
                exit 1
            fi
            # Check if wine-cachyos is installed or available in repos
            if pacman -Qi wine-cachyos &>/dev/null || pacman -Ss wine-cachyos | grep -q "^cachyos/wine-cachyos"; then
                echo "Found wine-cachyos package for CachyOS, using it instead of regular wine..."
                sudo pacman -S --needed \
                    wine-cachyos \
                    winetricks \
                    wget \
                    curl \
                    p7zip \
                    tar \
                    jq \
                    pv \
                    aria2 \
                    wine-mono \
                    wine-gecko \
                    lib32-nvidia-utils
            else
                echo "wine-cachyos not found, using regular wine package..."
                sudo pacman -S --needed \
                    wine \
                    winetricks \
                    wget \
                    curl \
                    p7zip \
                    tar \
                    jq \
                    pv \
                    aria2 \
                    wine-mono \
                    wine-gecko \
                    lib32-nvidia-utils
            fi
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
                aria2 \
                wine-mono \
                wine-gecko
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
                aria2 \
                wine-mono \
                wine-gecko
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
                aria2 \
                wine-mono \
                wine-gecko
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
    local repo="daegalus/wine-tkg-affinity"
    local filename="wine-tkg-affinity-fedorabuilt.tar.zst"

    echo "Installing $app..."
    
    # Kill any running wine processes
    wineserver -k
    
    # Create install directory
    mkdir -p "$directory"

    # Download and verify Wine binary
    echo "Downloading Wine binary..."
    release_info=$(curl -s "https://api.github.com/repos/$repo/releases/latest")
    download_url=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .browser_download_url")
    
    if [ -z "$download_url" ]; then
        echo "Error: Could not find download URL for $filename"
        exit 1
    fi

    # Download Wine binary with progress
    download_with_progress "$download_url" "$directory/$filename" "Wine binary"

    # Verify download
    if [ ! -f "$directory/$filename" ]; then
        echo "Error: Failed to download Wine binary"
        exit 1
    fi

    # Extract files
    echo "Extracting files..."
    echo "Extracting Wine binary..."
    
    # Create a temporary directory for extraction
    temp_dir="$directory/temp_extract"
    mkdir -p "$temp_dir"
    
    # Extract the tar.zst file to temp directory
    if ! tar --use-compress-program=zstd -xf "$directory/$filename" -C "$temp_dir"; then
        echo "Error: Failed to extract Wine binary"
        exit 1
    fi
    
    # Move the contents to the correct location
    if [ -d "$temp_dir/wine-tkg-affinity" ]; then
        # If the archive contains the wine-tkg-affinity directory
        mv "$temp_dir/wine-tkg-affinity" "$directory/"
    else
        # If the archive contains the contents directly
        mkdir -p "$directory/wine-tkg-affinity"
        mv "$temp_dir"/* "$directory/wine-tkg-affinity/"
    fi
    
    # Flatten directory if needed (move up contents if only one subdir)
    subdir_count=$(find "$directory/wine-tkg-affinity" -mindepth 1 -maxdepth 1 -type d | wc -l)
    file_count=$(find "$directory/wine-tkg-affinity" -mindepth 1 -maxdepth 1 | wc -l)
    if [ "$subdir_count" -eq 1 ] && [ "$file_count" -eq 1 ]; then
        only_subdir=$(find "$directory/wine-tkg-affinity" -mindepth 1 -maxdepth 1 -type d | head -n 1)
        echo "Flattening: moving contents of $only_subdir up to $directory/wine-tkg-affinity"
        mv "$only_subdir"/* "$directory/wine-tkg-affinity/"
        rmdir "$only_subdir"
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    rm -f "$directory/$filename"

    # Find the wine binary
    echo "Searching for Wine binary..."
    WINE=$(find "$directory/wine-tkg-affinity" -name "wine" -type f -executable | head -n 1)
    if [ -z "$WINE" ]; then
        echo "Error: Could not find Wine binary in the extracted files"
        echo "Directory contents:"
        find "$directory/wine-tkg-affinity" -type f -ls
        exit 1
    fi
    echo "Found Wine binary at: $WINE"

    # Download and extract WinMetadata
    echo "Downloading Windows metadata..."
    if ! download_with_progress "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata"; then
        echo "Warning: Failed to download Windows metadata, continuing without it..."
    else
        echo "Extracting Windows metadata..."
        if [ -f "$directory/Winmetadata.zip" ]; then
            mkdir -p "$directory/drive_c/windows/system32"
            if ! 7z x -y "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"; then
                echo "Warning: Failed to extract Windows metadata, continuing without it..."
            fi
            rm -f "$directory/Winmetadata.zip"
        fi
    fi

    # Configure Wine environment
    echo "Configuring Wine environment..."
    WINEPREFIX="$directory" "$WINE" winecfg -v win11
    
    # Always run winetricks, no matter what
    echo "Installing .NET Framework and dependencies..."
    export WINEPREFIX="$directory"
    export WINE="$WINE"
    export WINESERVER="$(dirname "$WINE")/wineserver"
    winetricks --unattended dotnet35
    winetricks --unattended dotnet48
    winetricks --unattended corefonts vcrun2022 allfonts
    winetricks renderer=vulkan

    # Configure .NET Framework
    echo "Configuring .NET Framework..."
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "mscoree" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "msvcp140" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "vcruntime140" /t REG_SZ /d "native" /f

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

    # Copy and run the installer
    echo "Starting installation..."
    cp "$HOME/.AffinityLinux_temp/affinity_installer.exe" "$directory/affinity_installer.exe"
    
    echo "Running Affinity installer..."
    echo "========================================================"
    echo "IMPORTANT: A new window should open with the Affinity installer."
    echo "Please follow these steps:"
    echo "1. Complete the installation process in the new window"
    echo "2. If you see any error messages, click 'No' to continue"
    echo "3. Wait for the installation to complete"
    echo "4. Come back to this terminal and press Enter"
    echo "========================================================"
    echo "Press Enter when the installation is complete..."
    
    # Run the installer with error handling
    if ! WINEPREFIX="$directory" "$WINE" "$directory/affinity_installer.exe"; then
        echo "Warning: Wine process exited with an error, but continuing..."
    fi
    
    # Wait for user to complete installation
    read -p "Press Enter when the installation is complete..."
    
    # Wait for Wine processes to finish
    echo "Waiting for installation to complete..."
    "$WINE" wineserver -w
    
    # Verify installation
    if [ ! -d "$directory/drive_c/Program Files/Affinity/$app_name 2" ]; then
        echo "Error: Affinity installation not found in expected location"
        echo "Please make sure the installation completed successfully"
        exit 1
    fi
    
    # Clean up installer
    rm -f "$directory/affinity_installer.exe"

    # Apply dark theme using curl instead of aria2c
    echo "Downloading Dark theme..."
    if ! curl -L -o "$directory/wine-dark-theme.reg" "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg"; then
        echo "Warning: Failed to download dark theme, skipping..."
    else
        if [ -f "$directory/wine-tkg-affinity/bin/regedit" ]; then
            WINEPREFIX="$directory" "$WINE" regedit "$directory/wine-dark-theme.reg"
        fi
        rm "$directory/wine-dark-theme.reg"
    fi

    # Remove old desktop entry if it exists
    rm -f "$HOME/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"

    # Create new desktop entry with absolute paths and proper quoting
    user_home="$HOME"
    wine_bin_path="$user_home/.AffinityLinux/wine-tkg-affinity/bin/wine"
    wine_prefix="$user_home/.AffinityLinux"
    affinity_exe="$user_home/.AffinityLinux/drive_c/Program Files/Affinity/$app_path"
    icon_path="$user_home/.local/share/icons/$icon_name"
    desktop_file="$user_home/.local/share/applications/$desktop_name.desktop"

    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Affinity $app_name
Comment=$comment
Icon=$icon_path
Path=$wine_prefix
Exec=env WINEPREFIX=$wine_prefix WINEDEBUG=-all "$wine_bin_path" "$affinity_exe"
Terminal=false
NoDisplay=false
StartupWMClass=$startup_wm
Type=Application
Categories=Graphics;
StartupNotify=true
EOF

    # Make the desktop entry executable
    chmod +x "$desktop_file"

    # Copy desktop entry to desktop
    cp "$desktop_file" "$user_home/Desktop/$desktop_name.desktop"
    chmod +x "$user_home/Desktop/$desktop_name.desktop"

    # Create MIME type definition
    mkdir -p ~/.local/share/mime/packages
    cat > ~/.local/share/mime/packages/affinity-$app_name.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-affinity-$app_name">
    <comment>Affinity $app_name Document</comment>
    <glob pattern="*.af$app_name"/>
    <glob pattern="*.af$app_name\#"/>
  </mime-type>
</mime-info>
EOF

    # Update MIME database
    update-mime-database ~/.local/share/mime

    # Update desktop database
    update-desktop-database ~/.local/share/applications

    # Set Wine configuration
    WINEPREFIX="$directory" "$WINE" winecfg -v win11
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "mscoree" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "mshtml" /t REG_SZ /d "native" /f

    echo "Installation of Affinity $app_name completed!"
}

# Function to update Affinity application
update_affinity() {
    local app=$1
    local directory="$HOME/.AffinityLinux"
    local repo="daegalus/wine-tkg-affinity"
    local filename="wine-tkg-affinity-fedorabuilt.tar.zst"

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
        *)
            echo "Invalid application choice"
            exit 1
            ;;
    esac

    # Check if installation exists
    if [ ! -d "$directory" ]; then
        echo "Error: Affinity installation not found at $directory"
        echo "Please install the application first."
        exit 1
    fi

    # Check if Wine binary exists
    if [ ! -f "$directory/wine-tkg-affinity/bin/wine" ]; then
        echo "Error: Wine binary not found at $directory/wine-tkg-affinity/bin/wine"
        echo "Please make sure the Wine binary was extracted correctly."
        exit 1
    fi

    # Download and verify new Wine binary
    echo "Downloading new Wine binary..."
    release_info=$(curl -s "https://api.github.com/repos/$repo/releases/latest")
    download_url=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .browser_download_url")
    [ -z "$download_url" ] && { echo "File not found in the latest release"; exit 1; }

    # Download new Wine binary with progress
    download_with_progress "$download_url" "$directory/$filename" "Wine binary"

    # Verify download
    github_size=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .size")
    local_size=$(wc -c < "$directory/$filename")

    if [ "$github_size" -ne "$local_size" ]; then
        echo "File sizes do not match: GitHub size: $github_size bytes, Local size: $local_size bytes"
        echo "Download $filename from $download_url move to $directory and hit any button to continue"
        read -n 1
    fi

    # Backup old Wine installation
    if [ -d "$directory/wine-tkg-affinity" ]; then
        mv "$directory/wine-tkg-affinity" "$directory/wine-tkg-affinity.bak"
    fi

    # Extract new Wine binary
    echo "Extracting new Wine binary..."
    
    # Create a temporary directory for extraction
    temp_dir="$directory/temp_extract"
    mkdir -p "$temp_dir"
    
    # Extract the tar.zst file to temp directory
    if ! tar --use-compress-program=zstd -xf "$directory/$filename" -C "$temp_dir"; then
        echo "Error: Failed to extract Wine binary"
        exit 1
    fi
    
    # Check what was extracted
    echo "Checking extracted content..."
    find "$temp_dir" -type d | sort
    
    # Create wine-tkg-affinity directory
    mkdir -p "$directory/wine-tkg-affinity"
    
    # Find any wine-tkg-affinity-git* directories in the extraction
    version_dir=$(find "$temp_dir" -maxdepth 2 -type d -name "wine-tkg-affinity-git*" | head -n 1)
    
    if [ -n "$version_dir" ]; then
        echo "Found versioned directory: $version_dir"
        # Move contents of versioned directory to wine-tkg-affinity
        cp -r "$version_dir"/* "$directory/wine-tkg-affinity/"
    else
        # Move the contents to the correct location
        if [ -d "$temp_dir/wine-tkg-affinity" ]; then
            # If the archive contains the wine-tkg-affinity directory
            cp -r "$temp_dir/wine-tkg-affinity"/* "$directory/wine-tkg-affinity/"
        else
            # If the archive contains the contents directly
            cp -r "$temp_dir"/* "$directory/wine-tkg-affinity/"
        fi
    fi
    
    # Create bin directory if it doesn't exist
    if [ ! -d "$directory/wine-tkg-affinity/bin" ] && [ -d "$directory/wine-tkg-affinity/bin64" ]; then
        echo "Creating bin symlink to bin64..."
        ln -sf "$directory/wine-tkg-affinity/bin64" "$directory/wine-tkg-affinity/bin"
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    rm -f "$directory/$filename"
    if [ -d "$directory/wine-tkg-affinity.bak" ]; then
        rm -rf "$directory/wine-tkg-affinity.bak"
    fi

    # Find the wine binary
    echo "Searching for Wine binary..."
    wine_found=false
    
    # Check potential locations
    for wine_path in "$directory/wine-tkg-affinity/bin/wine64" \
                     "$directory/wine-tkg-affinity/bin64/wine64" \
                     "$directory/wine-tkg-affinity/wine64" \
                     $(find "$directory/wine-tkg-affinity" -name "wine64" -type f -executable | head -n 1); do
        if [ -f "$wine_path" ]; then
            WINE="$wine_path"
            wine_found=true
            echo "Found Wine binary at: $WINE"
            
            # If the wine64 binary is not in the bin directory, create it
            if [[ "$WINE" != "$directory/wine-tkg-affinity/bin/wine64" ]]; then
                echo "Ensuring wine64 is in the bin directory..."
                mkdir -p "$directory/wine-tkg-affinity/bin"
                # Copy or symlink the wine binary to the bin directory
                if [ ! -f "$directory/wine-tkg-affinity/bin/wine64" ]; then
                    cp "$WINE" "$directory/wine-tkg-affinity/bin/"
                    chmod +x "$directory/wine-tkg-affinity/bin/wine64"
                    WINE="$directory/wine-tkg-affinity/bin/wine64"
                fi
            fi
            break
        fi
    done
    
    if [ "$wine_found" != true ]; then
        echo "Error: Could not find Wine64 binary in the extracted files"
        echo "Directory contents:"
        find "$directory/wine-tkg-affinity" -type f -ls
        exit 1
    fi

    # Download and extract WinMetadata
    echo "Downloading Windows metadata..."
    if ! download_with_progress "https://archive.org/download/win-metadata/WinMetadata.zip" "$directory/Winmetadata.zip" "Windows metadata"; then
        echo "Warning: Failed to download Windows metadata, continuing without it..."
    else
        echo "Extracting Windows metadata..."
        if [ -f "$directory/Winmetadata.zip" ]; then
            mkdir -p "$directory/drive_c/windows/system32"
            if ! 7z x -y "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"; then
                echo "Warning: Failed to extract Windows metadata, continuing without it..."
            fi
            rm -f "$directory/Winmetadata.zip"
        fi
    fi

    # Configure Wine environment
    echo "Configuring Wine environment..."
    WINEPREFIX="$directory" "$WINE" winecfg -v win11
    
    # Always run winetricks, no matter what
    echo "Installing .NET Framework and dependencies..."
    export WINEPREFIX="$directory"
    export WINE="$WINE"
    export WINESERVER="$(dirname "$WINE")/wineserver"
    winetricks --unattended dotnet35
    winetricks --unattended dotnet48
    winetricks --unattended corefonts vcrun2022 allfonts
    winetricks renderer=vulkan

    # Configure .NET Framework
    echo "Configuring .NET Framework..."
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "mscoree" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "mshtml" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "msvcp140" /t REG_SZ /d "native" /f
    WINEPREFIX="$directory" "$WINE" reg add "HKEY_CURRENT_USER\Software\Wine\DllOverrides" /v "vcruntime140" /t REG_SZ /d "native" /f

    # Check if installer exists in temp directory
    if [ ! -f "$HOME/.AffinityLinux_temp/affinity_installer.exe" ]; then
        echo "Error: Installer not found at $HOME/.AffinityLinux_temp/affinity_installer.exe"
        echo "Please make sure you've downloaded the installer and placed it in the correct location."
        exit 1
    fi

    # Copy and run the installer
    echo "Starting update..."
    cp "$HOME/.AffinityLinux_temp/affinity_installer.exe" "$directory/affinity_installer.exe"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to copy installer file"
        exit 1
    fi
    
    # Run the new installer
    echo "Running Affinity updater..."
    echo "Please follow the update wizard. Click 'Next' to proceed with the update."
    echo "If you see any error messages, click 'No' to continue."
    echo "Press Enter when the update is complete..."
    
    # Run the installer with error handling
    if ! WINEPREFIX="$directory" "$WINE" "$directory/affinity_installer.exe"; then
        echo "Warning: Wine process exited with an error, but continuing..."
    fi
    
    # Wait for user to complete update
    read -p "Press Enter when the update is complete..."
    
    # Wait for Wine processes to finish
    echo "Waiting for update to complete..."
    "$WINE" wineserver -w
    
    # Clean up installer if it exists
    if [ -f "$directory/affinity_installer.exe" ]; then
        rm "$directory/affinity_installer.exe"
    fi

    echo "Update of Affinity $app_name completed!"
}

# Function to uninstall Affinity application
uninstall_affinity() {
    local app=$1
    local directory="$HOME/.AffinityLinux"

    echo "Uninstalling $app..."
    
    # Set application-specific variables
    case $app in
        "Photo")
            app_name="Photo"
            desktop_name="AffinityPhoto"
            icon_name="AffinityPhoto.svg"
            ;;
        "Designer")
            app_name="Designer"
            desktop_name="AffinityDesigner"
            icon_name="AffinityDesigner.svg"
            ;;
        "Publisher")
            app_name="Publisher"
            desktop_name="AffinityPublisher"
            icon_name="AffinityPublisher.svg"
            ;;
        *)
            echo "Invalid application choice"
            exit 1
            ;;
    esac

    # Check if installation exists
    if [ ! -d "$directory" ]; then
        echo "Error: Affinity installation not found at $directory"
        echo "Please make sure the application is installed."
        exit 1
    fi

    # Kill any running wine processes
    wineserver -k

    # Remove desktop entries
    echo "Removing desktop entries..."
    rm -f ~/.local/share/applications/$desktop_name.desktop
    rm -f ~/Desktop/$desktop_name.desktop
    rm -f "$HOME/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"

    # Remove icon
    echo "Removing application icon..."
    rm -f "/home/$USER/.local/share/icons/$icon_name"

    # Remove application files
    echo "Removing application files..."
    if [ -d "$directory/drive_c/Program Files/Affinity/$app_name 2" ]; then
        rm -rf "$directory/drive_c/Program Files/Affinity/$app_name 2"
    fi

    # Check if other Affinity applications are installed
    local other_apps=0
    if [ -d "$directory/drive_c/Program Files/Affinity/Photo 2" ]; then
        other_apps=$((other_apps + 1))
    fi
    if [ -d "$directory/drive_c/Program Files/Affinity/Designer 2" ]; then
        other_apps=$((other_apps + 1))
    fi
    if [ -d "$directory/drive_c/Program Files/Affinity/Publisher 2" ]; then
        other_apps=$((other_apps + 1))
    fi

    # If this was the last application, remove the entire Wine prefix
    if [ $other_apps -eq 0 ]; then
        echo "Removing Wine prefix..."
        rm -rf "$directory"
    fi

    # Update desktop database
    update-desktop-database ~/.local/share/applications

    echo "Uninstallation of Affinity $app_name completed!"
}

# Main menu
echo "Affinity Linux Installation Script"
echo "================================="
echo "Select operation:"
echo "1) Install new Affinity application"
echo "2) Update existing Affinity application"
echo "3) Uninstall Affinity application"
read -p "Enter your choice (1-3): " operation_choice

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

        # Ask for the installer file before starting the installation
        echo "Please download the Affinity $app .exe from https://store.serif.com/account/licences/"
        echo "Then drag and drop the .exe file into this terminal window and press Enter."
        echo "The file will be automatically copied to the correct location and installed."
        read -p "Drag and drop the .exe file here: " installer_path

        # Remove quotes and handle special characters
        installer_path=$(echo "$installer_path" | sed -e "s/^'//" -e "s/'$//")
        
        # Verify the file exists
        if [ ! -f "$installer_path" ]; then
            echo "Error: File not found at $installer_path"
            echo "Please make sure the file exists and try again."
            exit 1
        fi

        # Create temporary directory for the installer
        temp_dir="$HOME/.AffinityLinux_temp"
        mkdir -p "$temp_dir"
        
        # Copy the file with proper handling of spaces and special characters
        cp -- "$installer_path" "$temp_dir/affinity_installer.exe"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to copy the installer file."
            exit 1
        fi

        # Install dependencies
        install_dependencies "$distro"

        # Install selected Affinity application
        install_affinity "$app"

        # Clean up temporary directory
        rm -rf "$temp_dir"
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
            *) 
                echo "Invalid choice"
                exit 1
                ;;
        esac

        # Ask for the installer file before starting the update
        echo "Please download the new Affinity $app .exe from https://store.serif.com/account/licences/"
        echo "Then drag and drop the .exe file into this terminal window and press Enter."
        echo "The file will be automatically copied to the correct location and installed."
        read -p "Drag and drop the .exe file here: " installer_path

        # Remove quotes and handle special characters
        installer_path=$(echo "$installer_path" | sed -e "s/^'//" -e "s/'$//")
        
        # Verify the file exists
        if [ ! -f "$installer_path" ]; then
            echo "Error: File not found at $installer_path"
            echo "Please make sure the file exists and try again."
            exit 1
        fi

        # Create temporary directory for the installer
        temp_dir="$HOME/.AffinityLinux_temp"
        mkdir -p "$temp_dir"
        
        # Copy the file with proper handling of spaces and special characters
        cp -- "$installer_path" "$temp_dir/affinity_installer.exe"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to copy the installer file."
            exit 1
        fi

        # Update selected Affinity application
        update_affinity "$app"

        # Clean up temporary directory
        rm -rf "$temp_dir"
        ;;
    3)
        echo "Select Affinity application to uninstall:"
        echo "1) Affinity Photo"
        echo "2) Affinity Designer"
        echo "3) Affinity Publisher"
        read -p "Enter your choice (1-3): " app_choice

        case $app_choice in
            1) app="Photo" ;;
            2) app="Designer" ;;
            3) app="Publisher" ;;
            *) 
                echo "Invalid choice"
                exit 1
                ;;
        esac

        # Confirm uninstallation
        read -p "Are you sure you want to uninstall Affinity $app? This will remove all application files. (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            echo "Uninstallation cancelled."
            exit 0
        fi

        # Uninstall selected Affinity application
        uninstall_affinity "$app"
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

echo -e "\nPress Enter to exit..."
read -n 1
exit 0 
