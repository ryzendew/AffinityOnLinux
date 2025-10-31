#!/bin/bash

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

# Download files
wget https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg -O "/home/$USER/.local/share/icons/AffinityPublisher.svg"
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
    wine_lib_dir="$directory/ElementalWarriorWine/lib/wine/vkd3d-proton/x86_64-windows"
    mkdir -p "$wine_lib_dir"
    if [ -f "$vkd3d_dir/x64/d3d12.dll" ]; then
        cp "$vkd3d_dir/x64/d3d12.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    if [ -f "$vkd3d_dir/x64/dxgi.dll" ]; then
        cp "$vkd3d_dir/x64/dxgi.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    if [ -f "$vkd3d_dir/d3d12.dll" ]; then
        cp "$vkd3d_dir/d3d12.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    if [ -f "$vkd3d_dir/x64/d3d12core.dll" ]; then
        cp "$vkd3d_dir/x64/d3d12core.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    if [ -f "$vkd3d_dir/d3d12core.dll" ]; then
        cp "$vkd3d_dir/d3d12core.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    if [ -f "$vkd3d_dir/dxgi.dll" ]; then
        cp "$vkd3d_dir/dxgi.dll" "$wine_lib_dir/" 2>/dev/null || true
    fi
    rm -rf "$vkd3d_dir"
    echo "vkd3d-proton installed successfully to Wine lib directory!"
fi

# Start the setup
echo "Download the Affinity Publisher .exe from https://store.serif.com/account/licences/"
echo "Once downloaded place the .exe in $directory and press any key when ready."
read -n 1

echo "Click No if you get any errors. Press any key to continue."
read -n 1

#Set windows version to 11
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory"/*.exe
rm "$directory"/affinity*.exe

#Wine dark theme
wget https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg -O "$directory/wine-dark-theme.reg"
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
rm "$directory/wine-dark-theme.reg"

#Remove Desktop entry created by wine
rm "/home/$USER/.local/share/applications/wine/Programs/Affinity Publisher 2.desktop"

# Create Desktop Entry
echo "[Desktop Entry]" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Name=Affinity Publisher" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Comment=Affinity Publisher is a desktop publishing application developed by Serif for iPadOS, macOS and Microsoft Windows." >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Icon=/home/$USER/.local/share/icons/AffinityPublisher.svg" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Path=$directory" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe\"" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Terminal=false" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "NoDisplay=false" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "StartupWMClass=publisher.exe" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Type=Application" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "Categories=Graphics;" >> ~/.local/share/applications/AffinityPublisher.desktop
echo "StartupNotify=true" >> ~/.local/share/applications/AffinityPublisher.desktop

cp ~/.local/share/applications/AffinityPublisher.desktop ~/Desktop/AffinityPublisher.desktop

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
