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
check_dependency "jq"

if [ -n "$missing_deps" ]; then
  echo "The following dependencies are missing: $missing_deps"
  echo "Please install them and rerun the script."
  exit 1
fi

echo "All dependencies are installed!"
sleep 2

directory="$HOME/.AffinityLinux"
repo="Twig6943/ElementalWarrior-Wine-binaries" #Owner/Repo
filename="ElementalWarriorWine.tar.gz" #Filename

#Kill wine
wineserver -k
# Create install directory
mkdir -p "$directory"

# Fetch the latest release information from GitHub
release_info=$(curl -s "https://api.github.com/repos/$repo/releases/latest")
download_url=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .browser_download_url")
[ -z "$download_url" ] && { echo "File not found in the latest release"; exit 1; }

# Download the specific release asset
wget -q "$download_url" -O "$directory/$filename" #Download wine binaries

# Check downloaded filesize matches repo
github_size=$(echo "$release_info" | jq -r ".assets[] | select(.name == \"$filename\") | .size")
local_size=$(wc -c < "$directory/$filename")


if [ "$github_size" -eq "$local_size" ]; then
    echo "File sizes match: $local_size bytes"
else
    echo "File sizes do not match: GitHub size: $github_size bytes, Local size: $local_size bytes"
    echo "Download $filename from $download_url move to $directory and hit any button to continue"
    read -n 1
fi

# Download files
wget https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg -O "/home/$USER/.local/share/icons/AffinityPhoto.svg"
wget https://archive.org/download/win-metadata/WinMetadata.zip -O "$directory/Winmetadata.zip"

# Extract wine binary
tar -xvzf "$directory/$filename" -C "$directory"

# Erase the ElementalWarriorWine.tar.gz
rm "$directory/$filename"

# WINETRICKS stuff
WINEPREFIX="$directory" winetricks --unattended dotnet35 dotnet48 corefonts
WINEPREFIX="$directory" winetricks renderer=vulkan

# Extract & delete WinMetadata.zip
7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32"
rm "$directory/Winmetadata.zip"
# Start the setup
echo "Download the Affinity Photo .exe from https://store.serif.com/account/licences/"
echo "Once downloaded place the .exe in $directory and press any key when ready."

read -n 1

echo "Click No if you get any errors. Press any key to continue."
read -n 1

#Set windows version to 11
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/wine" "$directory"/*.exe
rm "$directory"/affinity*.exe

#Wine dark theme
wget https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg -O "$directory/wine-dark-theme.reg"
WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg"
rm "$directory/wine-dark-theme.reg"

#Remove Desktop entry created by wine
rm "/home/$USER/.local/share/applications/wine/Programs/Affinity Photo 2.desktop"

# Create Desktop Entry
echo "[Desktop Entry]" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Name=Affinity Photo" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Comment=A powerful image editing software." >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Icon=/home/$USER/.local/share/icons/AffinityPhoto.svg" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Path=$directory" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe\"" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Terminal=false" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "NoDisplay=false" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "StartupWMClass=photo.exe" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Type=Application" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "Categories=Graphics;" >> ~/.local/share/applications/AffinityPhoto.desktop
echo "StartupNotify=true" >> ~/.local/share/applications/AffinityPhoto.desktop

cp ~/.local/share/applications/AffinityPhoto.desktop ~/Desktop/AffinityPhoto.desktop

# Copy to desktop
cp "$HOME/.local/share/applications/AffinityPhoto.desktop" "$HOME/Desktop/AffinityPhoto.desktop"

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
