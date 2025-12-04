# Hardware Acceleration

## vkd3d-proton and DXVK (Recommended)

**vkd3d-proton** and **DXVK** are modern alternatives to OpenCL that provide excellent hardware acceleration:

- **vkd3d-proton**: Direct3D 12 support (automatically configured)
- **DXVK**: Direct3D 11 support with excellent performance
- **More reliable** than OpenCL on many systems
- **Recommended** for better compatibility, especially on AMD and Intel GPUs

These are automatically configured by the installer and are the recommended method for hardware acceleration.

## OpenCL Support

OpenCL support is available with all Wine versions but may have compatibility issues depending on your GPU.

### GPU Compatibility

- **NVIDIA GPUs**: ✅ OpenCL works well. No known issues. Wine GPU bugs can typically be addressed.
- **AMD GPUs**: ⚠️ OpenCL may have issues. **Important:** I cannot fix AMD OpenCL issues or Wine GPU bugs as I do not have access to an AMD GPU for testing. Use vkd3d-proton or DXVK instead (recommended).
- **Intel GPUs**: ⚠️ OpenCL may have issues. **Important:** I cannot fix Intel GPU OpenCL issues or Wine GPU bugs as I do not have access to an Intel GPU for testing. Use vkd3d-proton or DXVK instead (recommended).

**Recommendation:** For AMD and Intel GPUs, use vkd3d-proton or DXVK instead of OpenCL for better reliability and performance.

## Additional Resources

For detailed OpenCL configuration, see the [OpenCL Guide](OpenCL-Guide.md).

## Support Limitations

- **AMD/Intel GPU Issues:** I cannot fix OpenCL or Wine GPU bugs for AMD/Intel GPUs as I do not have access to these GPUs for testing. Use vkd3d-proton or DXVK instead.

