# Hardware Acceleration

Affinity applications benefit significantly from hardware acceleration. The installer sets up everything automatically, but here's what you need to know about the different options.

## vkd3d-proton and DXVK (Recommended)

**vkd3d-proton** and **DXVK** are the recommended methods for hardware acceleration. They're more reliable than OpenCL on most systems and work well across different GPU vendors.

- **vkd3d-proton**: Handles Direct3D 12 calls, automatically configured by the installer
- **DXVK**: Translates Direct3D 11 to Vulkan, provides excellent performance

Both are set up automatically during installation, so you don't need to do anything extra. This is what most users should use, especially if you have an AMD or Intel GPU.

## OpenCL Support

OpenCL is available with all Wine versions, but your experience will depend on your GPU.

### GPU Compatibility

**NVIDIA GPUs:** OpenCL generally works well. If you run into issues, they're usually fixable.

**AMD GPUs:** OpenCL can be problematic. Since I don't have access to AMD hardware for testing, I can't debug OpenCL-specific issues on these GPUs. Your best bet is to stick with vkd3d-proton or DXVK, which are more reliable on AMD hardware.

**Intel GPUs:** Similar situation to AMD—OpenCL may not work reliably. Again, vkd3d-proton or DXVK are the safer choice here.

If you want to try OpenCL anyway, check out the [OpenCL Guide](OpenCL-Guide.md) for setup instructions. Just keep in mind that if things don't work, switching to vkd3d-proton/DXVK is usually the solution.

## What Gets Installed

The installer automatically:
- Configures vkd3d-proton for Direct3D 12 support
- Sets up DXVK for Direct3D 11 support
- Copies the necessary DLLs to each Affinity application directory
- Configures Wine to use Vulkan rendering

You can verify hardware acceleration is working by checking **Edit → Preferences → Performance** in any Affinity application.
