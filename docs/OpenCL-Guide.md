1. Install opencl Drivers for your gpu

    Ensure the gpu drivers and opencl drivers are installed for your GPU.
   
    e.g. for Arch & Nvidia:
   
    sudo pacman -S opencl-nvidia

3. Install VKD3D-Proton

    download vkd3d-proton to Lutris from [ProtonPlus](https://github.com/Vysp3r/ProtonPlus)


4. Configure Lutris

    Open Lutris and go to the game or app's configuration settings.
    Navigate to Runner Options.
    Select vkd3d-proton as the vkd3d version.
    Disable DXVK.

5. Launch Affinity Apps

Run the Affinity apps and verify OpenCL is working by checking the preferences for hardware acceleration.
