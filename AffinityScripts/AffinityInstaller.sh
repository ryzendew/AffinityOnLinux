# Copy and run the installer
echo "Starting installation..."
cp "$HOME/.AffinityLinux_temp/affinity_installer.exe" "$directory/affinity_installer.exe"

echo "Please set Windows version to Windows 11 in the winecfg window that will open."
echo "After setting Windows 11, close the winecfg window to continue."
WINEPREFIX="$directory" "$WINE" winecfg

echo "Running Affinity installer..."

# Copy and run the installer
echo "Starting update..."
cp "$HOME/.AffinityLinux_temp/affinity_installer.exe" "$directory/affinity_installer.exe"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy installer file"
    exit 1
fi

echo "Please set Windows version to Windows 11 in the winecfg window that will open."
echo "After setting Windows 11, close the winecfg window to continue."
WINEPREFIX="$directory" "$WINE" winecfg

# Run the new installer
