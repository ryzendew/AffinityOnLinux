#!/bin/bash

# Example: Set _distro variable manually for testing
# In practice, you might get this from a command like lsb_release or /etc/os-release
_distro=$(lsb_release -si)
_version=$(lsb_release -sr)

install_deps() {
    if [ "$_distro" = "ubuntu" ] || [ "$_distro" = "Mint" ]; then
        echo "Installing dependencies for $_distro"
        sudo apt install jq wine winetricks wget curl -y
   elif [ "$_distro" = "Pikaos" ]; then
        echo "Installing dependencies for $_distro"
        sudo apt install jq winehq-staging winetricks -y
    elif [ "$_distro" = "Arch" ] || [ "$_distro" = "CachyOS" ]; then
        echo "Installing dependencies for $_distro"
        sudo pacman -S wine-staging wget winetricks jq -y
    -y elif [ "$_distro" = "Fedora" ] || [ "$_distro" = "Nobara" ]; then
    if [ "$_version" = "40" ]; then echo "Installing dependencies for $_distro 40" 
         sudo dnf config-manager addrepo --from-repofile=https://dl.winehq.org/wine-builds/fedora/40/winehq.repo --overwrite
         sudo dnf install jq -y wget https://download.copr.fedorainfracloud.org/results/gloriouseggroll/nobara-40/fedora-40-x86_64/08247867-winetricks/winetricks-20240105-1.fc40.noarch.rpm
         sudo dnf install winetricks-20240105-1.fc40.noarch.rpm -y
         rm winetricks-20240105-1.fc40.noarch.rpm
    elif [ "$_version" = "41" ]; then echo "Installing dependencies for $_distro 41"
         sudo dnf config-manager addrepo --from-repofile=https://dl.winehq.org/wine-builds/fedora/41/winehq.repo --overwrite
         sudo dnf install jq -y wget https://download.copr.fedorainfracloud.org/results/gloriouseggroll/nobara-41/fedora-41-x86_64/08247867-winetricks/winetricks-20240105-1.fc41.noarch.rpm
         sudo dnf install winetricks-20240105-1.fc41.noarch.rpm -y
         rm  winetricks-20240105-1.fc41.noarch.rpm
    elif [ "$_distro" = "Suse" ]; then
        echo "Installing dependencies for $_distro"
        sudo zypper install -y jq winetricks wget wine-staging curl
    fi
}

# Main script execution
install_deps


directory="$HOME/.AffinityLinux"
repo="Twig6943/ElementalWarrior-Wine-binaries" #Owner/Repo
filename="ElementalWarriorWine.zip" #Filename

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
unzip "$directory/$filename" -d "$directory"

# Erase the ElementalWarriorWine.tar.gz
rm "$directory/$filename"

# WINETRICKS
WINEPREFIX="$directory" winetricks -q dotnet48 corefonts allfonts vcrun2015 renderer=vulkan --force

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
