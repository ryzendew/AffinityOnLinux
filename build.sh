#!/bin/bash

# Create a build directory if it doesn't exist
mkdir -p build

# Run pyinstaller
pyinstaller --onefile --windowed --name AffinityLinuxInstaller --icon=icons/Affinity.png AffinityScripts/AffinityLinuxInstaller.py --distpath ./build
