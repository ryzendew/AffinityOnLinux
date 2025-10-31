#!/bin/bash

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

# Check for required dependencies
missing_deps=""

check_dependency() {
  if ! command -v "$1" &> /dev/null; then
    missing_deps+="$1 "
  fi
}

check_dependency "wine"
check_dependency "winetricks"
check_dependency "wget"
check_dependency "curl"
check_dependency "7z"
check_dependency "tar"

if [ -n "$missing_deps" ]; then
  echo "The following dependencies are missing: $missing_deps"
  echo "Please install them and rerun the script."
  exit 1
fi

echo "All dependencies are installed!"
sleep 2

directory="$HOME/.AffinityLinux"
wine_url="https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
filename="ElementalWarriorWine-x86_64.tar.gz"

#Kill wine
wineserver -k
# Create install directory
mkdir -p "$directory"

# Download the specific Wine version
wget -q "$wine_url" -O "$directory/$filename"

# Download files and copy Affinity icon
script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
mkdir -p "/home/$USER/.local/share/icons"
if [ -f "$script_dir/icons/Affinity.png" ]; then
  cp "$script_dir/icons/Affinity.png" "/home/$USER/.local/share/icons/Affinity.png"
  echo "Copied Affinity icon to icons folder"
else
  echo "Warning: Affinity.png not found in $script_dir/icons/"
fi
wget https://archive.org/download/win-metadata/WinMetadata.zip -O "$directory/Winmetadata.zip"

# Extract wine binary
tar -xzf "$directory/$filename" -C "$directory"

# Find the actual Wine directory and create a symlink if needed
wine_dir=$(find "$directory" -name "ElementalWarriorWine*" -type d | head -1)
if [ -n "$wine_dir" ] && [ "$wine_dir" != "$directory/ElementalWarriorWine" ]; then
    echo "Creating Wine directory symlink..."
    ln -sf "$wine_dir" "$directory/ElementalWarriorWine"
fi

# Verify Wine binary exists
if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
    echo "Wine binary not found. Checking directory structure..."
    echo "Contents of $directory:"
    ls -la "$directory"
    if [ -n "$wine_dir" ]; then
        echo "Contents of $wine_dir:"
        ls -la "$wine_dir"
    fi
    exit 1
fi

# Erase the ElementalWarriorWine.tar.gz
rm "$directory/$filename"

# WINETRICKS stuff
WINEPREFIX="$directory" winetricks --unattended dotnet35 dotnet48 corefonts vcrun2022
WINEPREFIX="$directory" winetricks renderer=vulkan

# Extract & delete WinMetadata.zip
# Ensure the system32 directory exists before extraction
mkdir -p "$directory/drive_c/windows/system32"

if [ -f "$directory/Winmetadata.zip" ]; then
    if command -v 7z &> /dev/null; then
        7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" -y >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "Windows metadata extracted successfully"
        else
            echo "Warning: 7z extraction had issues, trying unzip..."
            unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1 || true
        fi
    elif command -v unzip &> /dev/null; then
        unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "Windows metadata extracted successfully"
        else
            echo "Warning: Failed to extract Windows metadata"
        fi
    else
        echo "Error: Neither 7z nor unzip is available to extract Windows metadata"
    fi
    rm -f "$directory/Winmetadata.zip"
else
    echo "Error: WinMetadata.zip was not downloaded successfully"
fi

# Download and install vkd3d-proton for OpenCL support
echo "Installing vkd3d-proton for OpenCL support..."
wget -q "https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst" -O "$directory/vkd3d-proton-2.14.1.tar.zst"

# Extract vkd3d-proton
if command -v unzstd &> /dev/null; then
    unzstd -f "$directory/vkd3d-proton-2.14.1.tar.zst" -o "$directory/vkd3d-proton.tar"
    tar -xf "$directory/vkd3d-proton.tar" -C "$directory"
    rm "$directory/vkd3d-proton.tar"
elif command -v zstd &> /dev/null && tar --help 2>&1 | grep -q "use-compress-program"; then
    tar --use-compress-program=zstd -xf "$directory/vkd3d-proton-2.14.1.tar.zst" -C "$directory"
else
    echo "Warning: Cannot extract .tar.zst file. Please install zstd. Skipping vkd3d-proton installation."
    rm -f "$directory/vkd3d-proton-2.14.1.tar.zst"
fi
rm -f "$directory/vkd3d-proton-2.14.1.tar.zst"

# Find and copy vkd3d-proton DLL files to Wine lib directory
vkd3d_dir=$(find "$directory" -type d -name "vkd3d-proton-*" | head -1)
if [ -n "$vkd3d_dir" ]; then
    # Create Wine lib/vkd3d-proton directory structure
    wine_lib_dir="$directory/ElementalWarriorWine/lib/wine/vkd3d-proton/x86_64-windows"
    mkdir -p "$wine_lib_dir"
    
    # Copy DLL files to Wine lib directory
    if [ -f "$vkd3d_dir/x64/d3d12.dll" ]; then
        cp "$vkd3d_dir/x64/d3d12.dll" "$wine_lib_dir/" 2>/dev/null || true
    elif [ -f "$vkd3d_dir/d3d12.dll" ]; then
        cp "$vkd3d_dir/d3d12.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    
    if [ -f "$vkd3d_dir/x64/d3d12core.dll" ]; then
        cp "$vkd3d_dir/x64/d3d12core.dll" "$wine_lib_dir/" 2>/dev/null || true
    elif [ -f "$vkd3d_dir/d3d12core.dll" ]; then
        cp "$vkd3d_dir/d3d12core.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    
    if [ -f "$vkd3d_dir/x64/dxgi.dll" ]; then
        cp "$vkd3d_dir/x64/dxgi.dll" "$wine_lib_dir/" 2>/dev/null || true
    elif [ -f "$vkd3d_dir/dxgi.dll" ]; then
        cp "$vkd3d_dir/dxgi.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    
    rm -rf "$vkd3d_dir"
    echo "vkd3d-proton installed successfully to Wine lib directory!"
fi

# Wine dark theme
wget https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg -O "$directory/wine-dark-theme.reg"
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
rm "$directory/wine-dark-theme.reg"

#Set windows version to 11
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true

# Start the setup
echo "Download the Affinity .exe installers from https://store.serif.com/account/licences/"
echo ""
echo "For each Affinity application (Photo, Designer, Publisher):"
echo "Drag and drop the .exe installer into this terminal and press Enter"
echo "Type 'done' when you've installed all applications"

while true; do
    echo ""
    echo "Drag and drop an Affinity .exe installer (or type 'done' to finish):"
    read installer_path
    
    if [ "$installer_path" = "done" ]; then
        break
    fi
    
    # Normalize the path
    installer_path=$(normalize_path "$installer_path")
    
    # Check if file exists and is readable
    if [ ! -f "$installer_path" ] || [ ! -r "$installer_path" ]; then
        echo "Invalid file path or file is not readable: $installer_path"
        continue
    fi
    
    # Get the filename from the path
    filename=$(basename "$installer_path")
    
    # Copy installer to Affinity directory
    echo "Copying installer..."
    cp "$installer_path" "$directory/$filename"
    
    echo "Click No if you get any errors. Press any key to continue."
    read -n 1
    
    # Run installer
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    
    # Clean up installer
    rm -f "$directory/$filename"
    rm -f "$directory"/affinity*.exe
    
    echo "Installation completed for $filename"
done

echo ""
echo "All installations completed!"

# Remove any existing desktop entries created by wine
rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity Photo 2.desktop"
rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity Designer 2.desktop"
rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity Publisher 2.desktop"

# Create Desktop Entry for Affinity (All in One)
icon_path="/home/$USER/.local/share/icons/Affinity.png"
if [ ! -f "$icon_path" ]; then
    # Fallback to Photo icon if Affinity.png not found
    icon_path="/home/$USER/.local/share/icons/AffinityPhoto.svg"
fi

echo "[Desktop Entry]" > ~/.local/share/applications/Affinity.desktop
echo "Name=Affinity Suite" >> ~/.local/share/applications/Affinity.desktop
echo "Comment=Photo, Designer, Publisher and more" >> ~/.local/share/applications/Affinity.desktop
echo "Icon=$icon_path" >> ~/.local/share/applications/Affinity.desktop
echo "Path=$directory" >> ~/.local/share/applications/Affinity.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Affinity/Affinity.exe\"" >> ~/.local/share/applications/Affinity.desktop
echo "Terminal=false" >> ~/.local/share/applications/Affinity.desktop
echo "NoDisplay=false" >> ~/.local/share/applications/Affinity.desktop
echo "Type=Application" >> ~/.local/share/applications/Affinity.desktop
echo "Categories=Graphics;" >> ~/.local/share/applications/Affinity.desktop
echo "StartupNotify=true" >> ~/.local/share/applications/Affinity.desktop
echo "StartupWMClass=affinity.exe" >> ~/.local/share/applications/Affinity.desktop
echo "Actions=Photo;Designer;Publisher;" >> ~/.local/share/applications/Affinity.desktop
echo "" >> ~/.local/share/applications/Affinity.desktop
echo "[Desktop Action Photo]" >> ~/.local/share/applications/Affinity.desktop
echo "Name=Affinity Photo" >> ~/.local/share/applications/Affinity.desktop
echo "Icon=/home/$USER/.local/share/icons/AffinityPhoto.svg" >> ~/.local/share/applications/Affinity.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe\"" >> ~/.local/share/applications/Affinity.desktop
echo "" >> ~/.local/share/applications/Affinity.desktop
echo "[Desktop Action Designer]" >> ~/.local/share/applications/Affinity.desktop
echo "Name=Affinity Designer" >> ~/.local/share/applications/Affinity.desktop
echo "Icon=/home/$USER/.local/share/icons/AffinityDesigner.svg" >> ~/.local/share/applications/Affinity.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Designer 2/Designer.exe\"" >> ~/.local/share/applications/Affinity.desktop
echo "" >> ~/.local/share/applications/Affinity.desktop
echo "[Desktop Action Publisher]" >> ~/.local/share/applications/Affinity.desktop
echo "Name=Affinity Publisher" >> ~/.local/share/applications/Affinity.desktop
echo "Icon=/home/$USER/.local/share/icons/AffinityPublisher.svg" >> ~/.local/share/applications/Affinity.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe\"" >> ~/.local/share/applications/Affinity.desktop

cp ~/.local/share/applications/Affinity.desktop ~/Desktop/Affinity.desktop

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

