# Changelog

## [2025-12-04] - Documentation Restructure and Updates

### Added

#### Merged Pull Requests
- **[#91](https://github.com/ryzendew/AffinityOnLinux/pull/91)** - Implement GPU detection and selection in installer for multi-GPU users
  - Added GPU detection functionality to help users with multiple GPUs select the correct one
  - Enhanced `AffinityLinuxInstaller.sh` with 212+ lines of GPU selection logic
  - Improves compatibility for laptops and systems with integrated + dedicated GPUs

#### New Documentation Structure
- **Created comprehensive documentation files** in new `docs/` folder
  - `INSTALLATION.md` - Complete installation guide for all methods
  - `SYSTEM-REQUIREMENTS.md` - Supported distributions and dependencies
  - `WINE-VERSIONS.md` - Wine version information and recommendations
  - `HARDWARE-ACCELERATION.md` - GPU acceleration options guide
  - `LEGACY-SCRIPTS.md` - Command-line installation scripts documentation
  - `CONTRIBUTING.md` - Contributing guidelines for the project

#### Enhanced Documentation
- **OpenCL Guide improvements**
  - Added Fedora/Nobara installation instructions for AMD GPUs
  - Added Arch Linux installation instructions for AMD GPUs
  - Complete rewrite with professional structure, verification steps, and troubleshooting
- **Python GUI Dependencies section** in README
  - Added collapsible details section with installation commands for all supported distributions

### Changed

#### Documentation Organization
- **Major README restructure**
  - Separated detailed content into dedicated documentation files
  - Cleaner, more navigable structure with organized documentation links
  - Maintained quick start guide in README for easy access
- **Wine version updates**
  - Updated supported Wine versions to 9.14 and 10.10 only
  - Removed references to 10.4, 10.4 v2, and 10.11
  - Updated all documentation to reflect current Wine version support
- **Hardware Acceleration guide rewrite**
  - More natural, professional tone
  - Better organization and flow
  - Clearer explanations of vkd3d-proton, DXVK, and OpenCL options
- **Known Issues comprehensive update**
  - Added all current GitHub issues (#89, #68, #53, #10, #41)
  - Organized by category (Application Crashes, Installation Issues, Distribution-Specific, etc.)
  - Added workarounds and links to GitHub issues
  - Better structure with clear sections

### Removed

#### Deprecated Documentation
- **Removed WARP.md** - Developer documentation file no longer needed
- **Removed OtherSoftware-on-Linux.md** - Content no longer relevant
- Removed references to deprecated files from README

### Fixed

#### PyQt6 Import Issues on Fedora
- **Fixed QSvgWidget import failure** on Fedora and other distributions where SVG support is in a separate package
  - Added graceful fallback when `PyQt6.QtSvgWidgets.QSvgWidget` is not available
  - Installer now continues to work even when SVG widget is missing (with warning)
  - Some icons may not display correctly when SVG widget is unavailable
- **Updated Fedora installation instructions** to include `python3-pyqt6-svg` package
  - Added to both README and installation documentation

#### Merged Pull Requests
- **[#90](https://github.com/ryzendew/AffinityOnLinux/pull/90)** - Fixed missing `fi` statement in shell script
  - Corrected syntax error in `AffinityLinuxInstaller.sh` that could cause script failures
  - Ensures proper script execution flow

#### Documentation Accuracy
- **Updated all cross-references** after file reorganization
- Fixed relative paths in documentation files after moving to `docs/` folder
- Updated Wine version references throughout all documentation files
- **Added window management crash issue** to known issues
  - Documented UI element moving causing crashes ([#108](https://github.com/ryzendew/Linux-Affinity-Installer/issues/108))
  - Clarified this is a Wine limitation that cannot be fixed
- **Added AppImage memory issue** to known issues
  - Documented excessive RAM usage and random crashes ([#106](https://github.com/ryzendew/Linux-Affinity-Installer/issues/106))
  - Noted this appears to be a random bug affecting the AppImage build
- **Added login/authentication issue** to known issues
  - Documented that logging into Affinity applications does not work due to Wine limitations
  - Clarified that applications work fully offline without authentication

### Technical Details

#### Files Modified
- `README.md` - Complete restructure with organized documentation links
- `docs/INSTALLATION.md` - New comprehensive installation guide
- `docs/SYSTEM-REQUIREMENTS.md` - New system requirements documentation
- `docs/WINE-VERSIONS.md` - Updated Wine version information
- `docs/HARDWARE-ACCELERATION.md` - Complete rewrite for better clarity
- `docs/OpenCL-Guide.md` - Professional rewrite with new installation instructions
- `docs/Known-issues.md` - Comprehensive update with current GitHub issues
- `docs/LEGACY-SCRIPTS.md` - New documentation file
- `docs/CONTRIBUTING.md` - New contributing guidelines

#### Files Removed
- `docs/WARP.md` - Deprecated developer documentation
- `docs/OtherSoftware-on-Linux.md` - No longer relevant

#### Statistics
- **New documentation files**: 6
- **Files removed**: 2
- **Files restructured**: 8
- **Documentation lines added**: ~500+
- **Documentation lines rewritten**: ~300+

---

### Summary

This update focused on improving documentation organization and accuracy:

1. **Better structure** - Separated long README into focused documentation files
2. **Cleaner organization** - All documentation now in dedicated `docs/` folder
3. **Updated information** - Wine versions, known issues, and installation instructions all current
4. **Professional presentation** - Rewritten guides with better clarity and natural tone
5. **Easier navigation** - Clear documentation links and organized sections

All documentation now reflects current project state and provides better user guidance.

---

## [2025-11-06] - Development Session

### Added

#### Enhanced Logging System
- **Comprehensive logging implementation** in `AffinityLinuxInstaller.py`
  - Added extensive logging throughout the installer script
  - Improved error tracking and debugging capabilities
  - Enhanced user feedback during installation processes
  - 290+ lines of logging code added

#### AMD GPU Support Enhancement
- **New launch option for Affinity v3 without OpenCL**
  - Added dedicated button/option for AMD users experiencing OpenCL compatibility issues
  - Created `AffinityWine10.17.sh` script (1,631 lines)
  - Provides alternative launch method for better AMD GPU compatibility

#### Funding and Sponsorship
- **Added funding support options**
  - Implemented Ko-fi integration
  - Added custom sponsorship link support
  - Created `.github/FUNDING.yml` configuration file

### Fixed

#### Font Rendering Issues
- **Resolved font display problems** across all Affinity application launchers
  - Fixed font issues in `AffinityDesigner.sh`
  - Fixed font issues in `AffinityPhoto.sh`
  - Fixed font issues in `AffinityPublisher.sh`
  - Fixed font issues in `Affinityv3.sh`
  - Fixed font issues in `AffinityLinuxInstaller.py`
  - Fixed font issues in `AffinityLinuxInstaller.sh`
  - Improved font handling and rendering consistency

### Changed

#### Documentation Updates
- **README.md improvements**
  - Updated project image/reference
  - Enhanced documentation content and clarity
  - Multiple iterative improvements to documentation structure
  - 122+ lines of documentation updates

#### Installer Enhancements
- **Major installer script improvements**
  - Significant code refactoring and feature additions
  - Enhanced user experience and error handling
  - Improved installation workflow
  - 626+ lines of code changes in `AffinityLinuxInstaller.py`

### Technical Details

#### Files Modified
- `AffinityScripts/AffinityLinuxInstaller.py` - Major updates with logging and features
- `AffinityScripts/AffinityWine10.17.sh` - New file for AMD OpenCL workaround
- `AffinityScripts/AffinityDesigner.sh` - Font fixes
- `AffinityScripts/AffinityPhoto.sh` - Font fixes
- `AffinityScripts/AffinityPublisher.sh` - Font fixes
- `AffinityScripts/Affinityv3.sh` - Font fixes
- `AffinityScripts/AffinityLinuxInstaller.sh` - Font fixes
- `README.md` - Documentation updates
- `.github/FUNDING.yml` - New funding configuration

#### Statistics
- **Total commits**: 11
- **Lines added**: ~2,000+
- **Lines modified**: ~100+
- **New files**: 2
- **Files modified**: 7

---

### Summary

This development session focused on improving the overall user experience and stability of the Affinity on Linux project. Key achievements include:

1. **Enhanced debugging capabilities** through comprehensive logging
2. **Better AMD GPU support** with dedicated OpenCL workaround
3. **Improved font rendering** across all application launchers
4. **Expanded funding options** for project sustainability
5. **Documentation improvements** for better user guidance

All changes maintain backward compatibility while adding new features and fixing critical issues.


