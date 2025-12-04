1. Install opencl Drivers for your gpu

    Ensure the gpu drivers and opencl drivers are installed for your GPU.

    **Arch Linux (NVIDIA):**
    ```bash
    sudo pacman -S opencl-nvidia
    ```

    **Arch Linux (AMD):**
    ```bash
    sudo pacman -S opencl-amd apr apr-util
    yay -S libxcrypt-compat
    ```

    **Fedora/Nobara (AMD):**
    ```bash
    sudo dnf install rocm-opencl apr apr-util zlib libxcrypt-compat libcurl libcurl-devel mesa-libGLU -y
    ```

3. Install VKD3D-Proton

    download vkd3d-proton to Lutris from [ProtonPlus](https://github.com/Vysp3r/ProtonPlus)


4. Configure Lutris

    Open Lutris and go to the game or app's configuration settings.
    Navigate to Runner Options.
    Select vkd3d-proton as the vkd3d version.
    Disable DXVK.

5. Launch Affinity Apps

Run the Affinity apps and verify OpenCL is working by checking the preferences for hardware acceleration.
