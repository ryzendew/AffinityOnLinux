#!/bin/bash

################################################################################
# Affinity Linux Installer - All-in-One Installation Script
# This script provides a unified installation interface for all Affinity
# applications with OpenCL support enabled.
################################################################################

# Check if script is executable, if not make it executable
if [ ! -x "$(readlink -f "$0")" ]; then
    echo "Making script executable..."
    chmod +x "$(readlink -f "$0")"
fi

# Ensure script is being run with bash
if [ -z "$BASH_VERSION" ]; then
    echo "This script must be run with bash"
    exit 1
fi

# ==========================================
# Constants and Configuration
# ==========================================

# Color codes for terminal output (if supported)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Helper functions for formatted output
print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_progress() {
    echo -e "${GREEN}  →${NC} $1"
}

# ==========================================
# Utility Functions
# ==========================================

# Function to download files with progress bar
download_file() {
    local url=$1
    local output=$2
    local description=$3
    
    print_progress "Downloading $description..."
    
    # Try curl first with progress bar
    if command -v curl &> /dev/null; then
        if curl -# -L "$url" -o "$output"; then
            return 0
        fi
    fi
    
    # Fallback to wget if curl fails or isn't available
    if command -v wget &> /dev/null; then
        if wget --progress=bar:force:noscroll "$url" -O "$output" 2>/dev/null; then
            return 0
        fi
    fi
    
    print_error "Failed to download $description"
    return 1
}

# ==========================================
# System Detection and Setup Functions
# ==========================================

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        print_error "Could not detect Linux distribution"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_header "Dependency Verification"
    print_info "Checking for required system dependencies..."
    
    local missing_deps=""
    
    for dep in wine winetricks wget curl 7z tar jq; do
        print_progress "Checking for $dep..."
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+="$dep "
            print_error "$dep is not installed"
        else
            print_success "$dep is installed"
        fi
    done
    
    # Check for zstd support (needed for vkd3d-proton)
    if ! command -v unzstd &> /dev/null && ! command -v zstd &> /dev/null; then
        missing_deps+="zstd "
        print_error "zstd or unzstd is not installed"
    else
        print_success "zstd support is available"
    fi
    
    if [ -n "$missing_deps" ]; then
        print_warning "Missing dependencies: $missing_deps"
        install_dependencies
    else
        print_success "All required dependencies are installed!"
    fi
    echo ""
}

# Function to install dependencies based on distribution
install_dependencies() {
    print_step "Installing dependencies for $DISTRO..."
    
    case $DISTRO in
        "ubuntu"|"linuxmint"|"pop"|"pikaos")
            sudo apt update
            sudo apt install -y wine winetricks wget curl p7zip-full tar jq zstd
            ;;
        "arch"|"cachyos")
            sudo pacman -S --needed wine winetricks wget curl p7zip tar jq zstd
            ;;
        "fedora"|"nobara")
            sudo dnf install -y wine winetricks wget curl p7zip p7zip-plugins tar jq zstd
            ;;
        "opensuse-tumbleweed"|"opensuse-leap")
            sudo zypper install -y wine winetricks wget curl p7zip tar jq zstd
            ;;
        *)
            print_error "Unsupported distribution: $DISTRO"
            print_info "Please install the following packages manually:"
            print_info "wine winetricks wget curl p7zip tar jq zstd"
            exit 1
            ;;
    esac
}

# ==========================================
# Wine Setup Functions
# ==========================================

# Function to verify Windows version
verify_windows_version() {
    local directory="$HOME/.AffinityLinux"
    print_progress "Setting Windows compatibility mode to Windows 11..."
    WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/winecfg" -v win11 >/dev/null 2>&1 || true
    print_success "Windows version configured"
    return 0
}

# Function to download and setup Wine
setup_wine() {
    print_header "Wine Binary Setup"
    print_info "Downloading and configuring the custom Wine build (ElementalWarriorWine)..."
    
    local directory="$HOME/.AffinityLinux"
    local wine_url="https://github.com/seapear/AffinityOnLinux/releases/download/Legacy/ElementalWarriorWine-x86_64.tar.gz"
    local filename="ElementalWarriorWine-x86_64.tar.gz"
    
    # Kill any running wine processes
    print_step "Stopping any running Wine processes..."
    wineserver -k 2>/dev/null || true
    print_success "Wine processes stopped"
    
    # Create install directory
    print_step "Creating installation directory: $directory"
    mkdir -p "$directory"
    print_success "Installation directory created"
    
    # Download the specific Wine version
    print_step "Downloading Wine binary from GitHub releases..."
    if download_file "$wine_url" "$directory/$filename" "Wine binaries"; then
        print_success "Wine binary downloaded successfully"
    else
        print_error "Failed to download Wine binary"
        exit 1
    fi
    
    # Extract wine binary
    print_step "Extracting Wine binary archive..."
    if tar -xzf "$directory/$filename" -C "$directory" 2>/dev/null; then
        print_success "Wine binary extracted successfully"
        rm "$directory/$filename"
    else
        print_error "Failed to extract Wine binary archive"
        exit 1
    fi
    
    # Find the actual Wine directory and create a symlink if needed
    print_step "Locating Wine installation directory..."
    wine_dir=$(find "$directory" -name "ElementalWarriorWine*" -type d | head -1)
    if [ -n "$wine_dir" ] && [ "$wine_dir" != "$directory/ElementalWarriorWine" ]; then
        print_info "Creating symlink for Wine directory..."
        ln -sf "$wine_dir" "$directory/ElementalWarriorWine"
        print_success "Symlink created: $directory/ElementalWarriorWine"
    fi
    
    # Verify Wine binary exists
    print_step "Verifying Wine binary exists..."
    if [ ! -f "$directory/ElementalWarriorWine/bin/wine" ]; then
        print_error "Wine binary not found at expected location"
        print_info "Checking directory structure..."
        echo "Contents of $directory:"
        ls -la "$directory" || true
        if [ -n "$wine_dir" ]; then
            echo "Contents of $wine_dir:"
            ls -la "$wine_dir" || true
        fi
        exit 1
    fi
    print_success "Wine binary verified: $directory/ElementalWarriorWine/bin/wine"
    
    # Create icons directory if it doesn't exist
    print_step "Setting up application icons..."
    mkdir -p "$HOME/.local/share/icons"
    
    # Download and setup additional files
    download_file "https://upload.wikimedia.org/wikipedia/commons/f/f5/Affinity_Photo_V2_icon.svg" "$HOME/.local/share/icons/AffinityPhoto.svg" "Affinity Photo icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/3/3c/Affinity_Designer_2-logo.svg" "$HOME/.local/share/icons/AffinityDesigner.svg" "Affinity Designer icon" || true
    download_file "https://upload.wikimedia.org/wikipedia/commons/9/9c/Affinity_Publisher_V2_icon.svg" "$HOME/.local/share/icons/AffinityPublisher.svg" "Affinity Publisher icon" || true
    
    # Copy Affinity icon from script directory to icons folder
    script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
    if [ -f "$script_dir/icons/Affinity.png" ]; then
        cp "$script_dir/icons/Affinity.png" "$HOME/.local/share/icons/Affinity.png" 2>/dev/null && \
        print_success "Copied Affinity icon to icons folder"
    fi
    
    # Download WinMetadata
    print_header "Windows Metadata Installation"
    print_info "Fetching Windows metadata files..."
    
    print_step "Downloading Windows metadata from archive.org..."
    # Use the same reliable method as individual scripts (wget with -q --show-progress)
    if wget -q --show-progress "https://archive.org/download/win-metadata/WinMetadata.zip" -O "$directory/Winmetadata.zip"; then
        # Verify the file was downloaded and has content (not zero bytes)
        if [ -s "$directory/Winmetadata.zip" ]; then
            print_success "Windows metadata downloaded successfully"
        else
            print_error "Downloaded file is empty or corrupted"
            rm -f "$directory/Winmetadata.zip"
        fi
    else
        print_warning "Failed to download Windows metadata (this may cause minor issues)"
        rm -f "$directory/Winmetadata.zip"
    fi
    
    # Ensure the system32 directory exists before extraction
    mkdir -p "$directory/drive_c/windows/system32"
    
    # Extract WinMetadata
    if [ -f "$directory/Winmetadata.zip" ] && [ -s "$directory/Winmetadata.zip" ]; then
        print_step "Extracting Windows metadata archive..."
        if command -v 7z &> /dev/null; then
            if 7z x "$directory/Winmetadata.zip" -o"$directory/drive_c/windows/system32" -y >/dev/null 2>&1; then
                print_success "Windows metadata extracted successfully using 7z"
            else
                print_warning "7z extraction had issues, trying unzip..."
                unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1 || true
                if [ $? -eq 0 ]; then
                    print_success "Windows metadata extracted using unzip"
                else
                    print_error "Extraction failed with both 7z and unzip. File may be corrupted."
                    print_info "You may need to manually download WinMetadata.zip and extract it"
                fi
            fi
        elif command -v unzip &> /dev/null; then
            if unzip -o "$directory/Winmetadata.zip" -d "$directory/drive_c/windows/system32" >/dev/null 2>&1; then
                print_success "Windows metadata extracted successfully using unzip"
            else
                print_error "Failed to extract Windows metadata"
                print_info "The downloaded file may be corrupted. Please check your internet connection and try again."
            fi
        else
            print_error "Neither 7z nor unzip is available to extract Windows metadata"
            print_info "Please install either 7z or unzip and rerun the script"
        fi
        
        print_step "Cleaning up metadata archive..."
        rm -f "$directory/Winmetadata.zip"
        print_success "Archive removed"
    else
        print_warning "WinMetadata.zip was not downloaded successfully or is corrupted"
        print_info "Installation will continue, but some Windows metadata features may not work"
    fi
    
    # Download and install vkd3d-proton for OpenCL support
    print_header "OpenCL Support Setup"
    print_info "Installing vkd3d-proton for hardware acceleration and OpenCL support..."
    print_info "This enables GPU acceleration features in Affinity applications"
    
    local vkd3d_url="https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v2.14.1/vkd3d-proton-2.14.1.tar.zst"
    local vkd3d_filename="vkd3d-proton-2.14.1.tar.zst"
    
    print_step "Downloading vkd3d-proton v2.14.1 from GitHub..."
    if download_file "$vkd3d_url" "$directory/$vkd3d_filename" "vkd3d-proton"; then
        print_success "vkd3d-proton downloaded successfully"
    else
        print_error "Failed to download vkd3d-proton"
        print_warning "OpenCL support may not work correctly"
    fi
    
    # Extract vkd3d-proton
    print_step "Extracting vkd3d-proton archive..."
    extracted=false
    if command -v unzstd &> /dev/null; then
        if unzstd -f "$directory/$vkd3d_filename" -o "$directory/vkd3d-proton.tar" 2>/dev/null; then
            if tar -xf "$directory/vkd3d-proton.tar" -C "$directory" 2>/dev/null; then
                rm "$directory/vkd3d-proton.tar"
                extracted=true
                print_success "vkd3d-proton extracted using unzstd"
            fi
        fi
    elif command -v zstd &> /dev/null && tar --help 2>&1 | grep -q "use-compress-program"; then
        if tar --use-compress-program=zstd -xf "$directory/$vkd3d_filename" -C "$directory" 2>/dev/null; then
            extracted=true
            print_success "vkd3d-proton extracted using zstd with tar"
        fi
    fi
    
    if [ "$extracted" = false ]; then
        print_error "Cannot extract .tar.zst file. Please install zstd (e.g., sudo pacman -S zstd)"
        print_warning "Skipping vkd3d-proton installation. OpenCL will not work!"
        rm -f "$directory/$vkd3d_filename"
    else
        rm -f "$directory/$vkd3d_filename"
        
        # Extract vkd3d-proton DLLs for later use (will be copied to Affinity directory after installation)
        local vkd3d_dir=$(find "$directory" -type d -name "vkd3d-proton-*" | head -1)
        if [ -n "$vkd3d_dir" ]; then
            # Store DLLs in a temporary location for later copying
            local vkd3d_temp="$directory/vkd3d_dlls"
            mkdir -p "$vkd3d_temp"
            
            print_step "Extracting vkd3d-proton DLLs..."
            # Copy DLL files to temp location (typical locations: x64/ or root)
            dll_count=0
            if [ -f "$vkd3d_dir/x64/d3d12.dll" ]; then
                cp "$vkd3d_dir/x64/d3d12.dll" "$vkd3d_temp/" 2>/dev/null && ((dll_count++))
            elif [ -f "$vkd3d_dir/d3d12.dll" ]; then
                cp "$vkd3d_dir/d3d12.dll" "$vkd3d_temp/" 2>/dev/null && ((dll_count++))
            fi
            
            if [ -f "$vkd3d_dir/x64/d3d12core.dll" ]; then
                cp "$vkd3d_dir/x64/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null && ((dll_count++))
            elif [ -f "$vkd3d_dir/d3d12core.dll" ]; then
                cp "$vkd3d_dir/d3d12core.dll" "$vkd3d_temp/" 2>/dev/null && ((dll_count++))
            fi
            
            # Also install to Wine library directory
            wine_lib_dir="$directory/ElementalWarriorWine/lib/wine/vkd3d-proton/x86_64-windows"
            mkdir -p "$wine_lib_dir"
            if [ -f "$vkd3d_temp/d3d12.dll" ]; then
                cp "$vkd3d_temp/d3d12.dll" "$wine_lib_dir/" 2>/dev/null || true
            fi
            if [ -f "$vkd3d_temp/d3d12core.dll" ]; then
                cp "$vkd3d_temp/d3d12core.dll" "$wine_lib_dir/" 2>/dev/null || true
            fi
            
            # Remove extracted vkd3d-proton directory
            rm -rf "$vkd3d_dir"
            if [ $dll_count -gt 0 ]; then
                print_success "Extracted $dll_count DLL file(s) for OpenCL support"
            fi
        else
            print_warning "Could not find vkd3d-proton directory after extraction"
        fi
    fi
    
    # Setup Wine
    print_header "Wine Configuration"
    print_info "Installing required Windows libraries and configuring Wine..."
    
    print_step "Installing .NET Framework 3.5..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet35 >/dev/null 2>&1 || true
    print_progress ".NET 3.5 installation attempted"
    
    print_step "Installing .NET Framework 4.8..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout dotnet48 >/dev/null 2>&1 || true
    print_progress ".NET 4.8 installation attempted"
    
    print_step "Installing Windows core fonts..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout corefonts >/dev/null 2>&1 || true
    print_progress "Core fonts installation attempted"
    
    print_step "Installing Visual C++ Redistributables 2022..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout vcrun2022 >/dev/null 2>&1 || true
    print_progress "VC++ 2022 installation attempted"
    
    print_step "Installing MSXML 3.0..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout msxml3 >/dev/null 2>&1 || true
    print_progress "MSXML 3.0 installation attempted"
    
    print_step "Installing MSXML 6.0..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout msxml6 >/dev/null 2>&1 || true
    print_progress "MSXML 6.0 installation attempted"
    
    print_step "Configuring Wine to use Vulkan renderer..."
    WINEPREFIX="$directory" winetricks --unattended --force --no-isolate --optout renderer=vulkan >/dev/null 2>&1 || true
    print_success "Wine configured with Vulkan renderer"
    
    print_info "Note: The above installations may take several minutes. Errors are normal if components are already installed."
    
    # Set and verify Windows version to 11
    verify_windows_version
    
    # Apply dark theme
    print_step "Applying Wine dark theme..."
    if download_file "https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg" "$directory/wine-dark-theme.reg" "dark theme"; then
        WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$directory/wine-dark-theme.reg" >/dev/null 2>&1 || true
        rm -f "$directory/wine-dark-theme.reg"
        print_success "Dark theme applied to Wine"
    else
        print_warning "Could not download dark theme registry file"
    fi
    
    print_success "Wine setup completed successfully!"
    echo ""
}

# ==========================================
# Affinity Installation Functions
# ==========================================

# Function to configure OpenCL support for an application
configure_opencl() {
    local app_dir=$1
    local app_name=$2
    local directory="$HOME/.AffinityLinux"
    local wine_lib_dir="$directory/ElementalWarriorWine/lib/wine/vkd3d-proton/x86_64-windows"
    local vkd3d_temp="$directory/vkd3d_dlls"
    
    if [ -d "$app_dir" ] && [ -d "$wine_lib_dir" ]; then
        print_info "Configuring OpenCL support for $app_name..."
        dll_copied=0
        
        # Try to copy from temp location first, then fallback to wine lib directory
        if [ -f "$vkd3d_temp/d3d12.dll" ]; then
            if cp "$vkd3d_temp/d3d12.dll" "$app_dir/" 2>/dev/null; then
                print_progress "Copied d3d12.dll to $app_name directory"
                ((dll_copied++))
            fi
        elif [ -f "$wine_lib_dir/d3d12.dll" ]; then
            if cp "$wine_lib_dir/d3d12.dll" "$app_dir/" 2>/dev/null; then
                print_progress "Copied d3d12.dll to $app_name directory"
                ((dll_copied++))
            fi
        fi
        
        if [ -f "$vkd3d_temp/d3d12core.dll" ]; then
            if cp "$vkd3d_temp/d3d12core.dll" "$app_dir/" 2>/dev/null; then
                print_progress "Copied d3d12core.dll to $app_name directory"
                ((dll_copied++))
            fi
        elif [ -f "$wine_lib_dir/d3d12core.dll" ]; then
            if cp "$wine_lib_dir/d3d12core.dll" "$app_dir/" 2>/dev/null; then
                print_progress "Copied d3d12core.dll to $app_name directory"
                ((dll_copied++))
            fi
        fi
        
        if [ $dll_copied -gt 0 ]; then
            print_success "Copied $dll_copied OpenCL DLL file(s) to $app_name directory"
        fi
        
        print_info "Configuring Wine DLL overrides for OpenCL support..."
        reg_file="$directory/dll_overrides.reg"
        {
            echo "REGEDIT4"
            echo "[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]"
            echo "\"d3d12\"=\"native\""
            echo "\"d3d12core\"=\"native\""
        } > "$reg_file"
        
        if WINEPREFIX="$directory" "$directory/ElementalWarriorWine/bin/regedit" "$reg_file" >/dev/null 2>&1; then
            print_success "DLL overrides configured in Wine registry"
        else
            print_warning "Could not apply DLL overrides (OpenCL may not work)"
        fi
        
        rm -f "$reg_file"
        
        if [ $dll_copied -gt 0 ]; then
            print_success "OpenCL support fully configured for $app_name!"
        fi
    else
        if [ ! -d "$app_dir" ]; then
            print_warning "$app_name installation directory not found. OpenCL configuration skipped."
        fi
    fi
}

# Function to create desktop entry
create_desktop_entry() {
    local app_name=$1
    local app_path=$2
    local icon_path=$3
    local desktop_file="$HOME/.local/share/applications/Affinity$app_name.desktop"
    
    echo "[Desktop Entry]" > "$desktop_file"
    echo "Name=Affinity $app_name" >> "$desktop_file"
    echo "Comment=A powerful $app_name software." >> "$desktop_file"
    echo "Icon=$icon_path" >> "$desktop_file"
    echo "Path=$HOME/.AffinityLinux" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$HOME/.AffinityLinux $HOME/.AffinityLinux/ElementalWarriorWine/bin/wine \"$app_path\"" >> "$desktop_file"
    echo "Terminal=false" >> "$desktop_file"
    echo "NoDisplay=false" >> "$desktop_file"
    echo "StartupWMClass=${app_name,,}.exe" >> "$desktop_file"
    echo "Type=Application" >> "$desktop_file"
    echo "Categories=Graphics;" >> "$desktop_file"
    echo "StartupNotify=true" >> "$desktop_file"
}

# Function to create Affinity desktop entry
create_all_in_one_desktop_entry() {
    local icon_path=$1
    local desktop_file="$HOME/.local/share/applications/Affinity.desktop"
    local directory="$HOME/.AffinityLinux"
    
    echo "[Desktop Entry]" > "$desktop_file"
    echo "Name=Affinity" >> "$desktop_file"
    echo "Comment=The unified Affinity application for photo editing, design, and publishing" >> "$desktop_file"
    echo "Icon=$icon_path" >> "$desktop_file"
    echo "Path=$directory" >> "$desktop_file"
    echo "Exec=env WINEPREFIX=$directory $directory/ElementalWarriorWine/bin/wine \"$directory/drive_c/Program Files/Affinity/Affinity/Affinity.exe\"" >> "$desktop_file"
    echo "Terminal=false" >> "$desktop_file"
    echo "NoDisplay=false" >> "$desktop_file"
    echo "Type=Application" >> "$desktop_file"
    echo "Categories=Graphics;" >> "$desktop_file"
    echo "StartupNotify=true" >> "$desktop_file"
    echo "StartupWMClass=affinity.exe" >> "$desktop_file"
}

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

# Function to install Affinity app
install_affinity() {
    local app_name=$1
    local directory="$HOME/.AffinityLinux"
    
    print_header "Affinity $app_name Installation"
    print_info "You will now install Affinity $app_name using its Windows installer"
    
    # Verify Windows version before installation
    verify_windows_version
    
    echo ""
    print_step "Please download the Affinity $app_name installer (.exe) from:"
    echo -e "  ${CYAN}https://store.serif.com/account/licences/${NC}"
    echo ""
    print_step "Once downloaded, drag and drop the installer into this terminal and press Enter:"
    read installer_path
    
    # Normalize the path
    installer_path=$(normalize_path "$installer_path")
    
    # Check if file exists and is readable
    if [ ! -f "$installer_path" ] || [ ! -r "$installer_path" ]; then
        print_error "Invalid file path or file is not readable: $installer_path"
        return 1
    fi
    
    # Get the filename from the path
    local filename=$(basename "$installer_path")
    
    # Copy installer to Affinity directory
    print_step "Copying installer to installation directory..."
    cp "$installer_path" "$directory/$filename"
    print_success "Installer copied"
    
    # Run installer
    print_step "Launching Affinity $app_name installer..."
    print_info "Follow the installation wizard in the window that opens"
    print_warning "If you encounter any errors during installation, click 'No' to continue"
    print_info "Press any key to start the installation..."
    read -n 1 -s
    echo ""
    
    # Run installer with debug messages suppressed
    WINEPREFIX="$directory" WINEDEBUG=-all "$directory/ElementalWarriorWine/bin/wine" "$directory/$filename"
    
    # Clean up installer
    print_step "Cleaning up installer file..."
    rm -f "$directory/$filename"
    print_success "Installer file removed"
    
    # Configure OpenCL support based on which app was installed
    print_header "Post-Installation Configuration"
    print_info "Applying final configuration settings..."
    
    case $app_name in
        "Photo")
            configure_opencl "$directory/drive_c/Program Files/Affinity/Photo 2" "Affinity Photo"
            ;;
        "Designer")
            configure_opencl "$directory/drive_c/Program Files/Affinity/Designer 2" "Affinity Designer"
            ;;
        "Publisher")
            configure_opencl "$directory/drive_c/Program Files/Affinity/Publisher 2" "Affinity Publisher"
            ;;
        "Add")
            configure_opencl "$directory/drive_c/Program Files/Affinity/Affinity" "Affinity"
            ;;
    esac
    
    # Remove Wine's default desktop entry
    print_step "Removing default Wine desktop entry..."
    rm -f "/home/$USER/.local/share/applications/wine/Programs/Affinity $app_name 2.desktop"
    print_success "Default entry removed"
    
    # Create desktop entry
    print_step "Creating custom desktop entry..."
    case $app_name in
        "Photo")
            create_desktop_entry "Photo" "$directory/drive_c/Program Files/Affinity/Photo 2/Photo.exe" "$HOME/.local/share/icons/AffinityPhoto.svg"
            ;;
        "Designer")
            create_desktop_entry "Designer" "$directory/drive_c/Program Files/Affinity/Designer 2/Designer.exe" "$HOME/.local/share/icons/AffinityDesigner.svg"
            ;;
        "Publisher")
            create_desktop_entry "Publisher" "$directory/drive_c/Program Files/Affinity/Publisher 2/Publisher.exe" "$HOME/.local/share/icons/AffinityPublisher.svg"
            ;;
        "Add")
            # Create Affinity desktop entry
            icon_path="$HOME/.local/share/icons/Affinity.png"
            if [ ! -f "$icon_path" ]; then
                # Fallback: try to copy from script directory if not already copied
                script_dir="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
                if [ -f "$script_dir/icons/Affinity.png" ]; then
                    cp "$script_dir/icons/Affinity.png" "$icon_path"
                    print_success "Copied Affinity icon to icons folder"
                else
                    print_warning "Affinity.png not found, using Photo icon as fallback"
                    icon_path="$HOME/.local/share/icons/AffinityPhoto.svg"
                fi
            fi
            create_all_in_one_desktop_entry "$icon_path"
            ;;
    esac
    
    # Create desktop shortcut
    desktop_file="$HOME/.local/share/applications/Affinity${app_name}.desktop"
    if [ "$app_name" = "Add" ]; then
        desktop_file="$HOME/.local/share/applications/Affinity.desktop"
    fi
    mkdir -p ~/Desktop
    cp "$desktop_file" ~/Desktop/ 2>/dev/null || true
    print_success "Desktop shortcut created"
    
    print_success "Affinity $app_name installation completed!"
    echo ""
    print_info "You can now launch Affinity $app_name from your application menu or desktop shortcut."
    print_info "OpenCL hardware acceleration should be enabled. You can verify this in:"
    echo -e "  ${CYAN}•${NC} Affinity Preferences → Performance → Hardware Acceleration"
    echo ""
}

# ==========================================
# User Interface Functions
# ==========================================

# Function to show special thanks
show_special_thanks() {
    print_header "Special Thanks"
    echo "Ardishco (github.com/raidenovich)"
    echo "Deviaze"
    echo "Kemal"
    echo "Jacazimbo <3"
    echo "Kharoon"
    echo "Jediclank134"
    echo ""
}

# Main menu
show_menu() {
    clear
    print_header "Affinity Linux Installer"
    echo ""
    echo -e "${BOLD}Available Applications:${NC}"
    echo ""
    echo -e "  ${GREEN}1.${NC} ${BOLD}Affinity${NC} (Unified Application)"
    echo -e "      ${CYAN}The new unified Affinity application that combines Photo, Designer," 
    echo -e "      Publisher, and more into a single modern interface.${NC}"
    echo ""
    echo -e "  ${GREEN}2.${NC} ${BOLD}Affinity Photo${NC}"
    echo -e "      ${CYAN}Professional photo editing and image manipulation software with" 
    echo -e "      advanced tools for photographers and digital artists.${NC}"
    echo ""
    echo -e "  ${GREEN}3.${NC} ${BOLD}Affinity Designer${NC}"
    echo -e "      ${CYAN}Vector graphic design software for creating illustrations, logos," 
    echo -e "      UI designs, print projects, and mock-ups.${NC}"
    echo ""
    echo -e "  ${GREEN}4.${NC} ${BOLD}Affinity Publisher${NC}"
    echo -e "      ${CYAN}Desktop publishing application for creating professional layouts," 
    echo -e "      magazines, books, and print materials.${NC}"
    echo ""
    echo -e "  ${GREEN}5.${NC} ${BOLD}Show Special Thanks${NC}"
    echo ""
    echo -e "  ${GREEN}6.${NC} ${BOLD}Exit${NC}"
    echo ""
    echo -n -e "${BOLD}Please select an option (1-6): ${NC}"
}

# ==========================================
# Main Script
# ==========================================

main() {
    print_header "Affinity Linux Installer - Initialization"
    
    # Detect distribution
    detect_distro
    print_info "Detected distribution: $DISTRO $VERSION"
    echo ""
    
    # Check and install dependencies
    check_dependencies
    
    # Setup Wine (only once)
    setup_wine
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                install_affinity "Add"
                ;;
            2)
                install_affinity "Photo"
                ;;
            3)
                install_affinity "Designer"
                ;;
            4)
                install_affinity "Publisher"
                ;;
            5)
                show_special_thanks
                ;;
            6)
                print_header "Thank You"
                print_success "Thank you for using the Affinity Installation Script!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select a number between 1 and 6."
                ;;
        esac
        
        if [ "$choice" != "6" ]; then
            echo ""
            read -n 1 -s -r -p "Press any key to continue..."
        fi
    done
}

# Run main function
main
