# Changelog

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


