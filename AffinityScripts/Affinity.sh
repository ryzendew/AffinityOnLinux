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
wine_url="https://github.com/ryzendew/ElementalWarrior-Wine-binaries/releases/download/Release/ElementalWarriorWine-x86_64.zip"
filename="ElementalWarriorWine-x86_64.zip"

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
unzip -o "$directory/$filename" -d "$directory"

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

# Erase the ElementalWarriorWine.zip
rm "$directory/$filename"

# WINETRICKS stuff
WINEPREFIX="$directory" winetricks --unattended dotnet35 dotnet48 corefonts vcrun2022 allfonts
WINEPREFIX="$directory" winetricks renderer=vulkan

# Extract & delete WinMetadata.zip
7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"
rm "$directory/Winmetadata.zip"

# Wine dark theme
wget https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg -O "$directory/wine-dark-theme.reg"
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
rm "$directory/wine-dark-theme.reg"

#Set windows version to 11
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true

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
echo "Name=Affinity" >> ~/.local/share/applications/Affinity.desktop
echo "Comment=Photo, Designer, Publisher and more" >> ~/.local/share/applications/Affinity.desktop
echo "Icon=$icon_path" >> ~/.local/share/applications/Affinity.desktop
echo "Path=$directory" >> ~/.local/share/applications/Affinity.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe\"" >> ~/.local/share/applications/Affinity.desktop
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

