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

# Download files
wget https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg -O "/home/$USER/.local/share/icons/AffinityPublisher.svg"
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

# Extract & delete WinMetadata.zip
7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"
rm "$directory/Winmetadata.zip"
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
