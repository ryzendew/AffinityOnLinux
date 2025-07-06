## How to Install Affinity Wine

Head to the github and Download the newest release [Here](https://github.com/Twig6943/ElementalWarrior-wine-binaries/releases) 

## Installing Heroic Game Launcher flathub

```
flatpak install flathub com.heroicgameslauncher.hgl
```
## Fedora 

```
sudo dnf in lutris
```
## Arch Linux

```
sudo pacman -S lutris
```
## Ubuntu/Debian

```
sudo apt install lutris
```
## Installing Affinity Linux's Prebuilt Wine

Extract the Elemental Warrior's Pre-built wine binaries to Heroic/Lutris wine directory

```
/home/USER/.config/heroic/tools/wine
```

## Flatpak's Wine location

```
/home/USER/.var/app/com.heroicgameslauncher.hgl/config/heroic/tools/wine
```
## Settings Up Heroic/Lutris For Affinity

Open up Heroic/lutris and then click on 

```
add game
``` 

Or for Lutris the 

```
+ Button
``` 
and at the bottom 

```
Add Locally Install Game
```

Name it According to the Affinity app you are using

```
Affinity Photo
```

```
Affinity Designer
```
```
Affinity Publisher
```
## Setting the Wine Version

Set the wine version to ElementalWarriorWine

## Selecting the Programs .exe According to what you Want to Install

Select the setup .exe you've downloaded from affinity's website as the executable

Click 
```
Finish
```
## Initialize the prefix

In order to initialize the prefix run the setup file from heroic. (It'll probably crash wait for it to crash if it somehow opens up close it yourself)

## Setting Up Affinity Wine Settings and Winetricks

* Right click on affinity on heroic and open up its settings

* Scroll down until you see winetricks & then click on it

* Search & install these dependencies;
```
dotnet48
```
```
corefonts
```
(Wait while its installing the dependencies. Its %90 not stuck but rather taking its time!!!)

Click on 
```
OPEN WINETRICKS GUI
```
Select 
```
Select the default wineprefix
```
Select 
```
Change settings
```
Toggle 
```
win11
```
Toggle 

```
renderer=vulkan
```
and click OK

Keep pressing "Cancel" till the winetricks window closes

Close heroic games launcher's settings window

## Placing WinMetadata

Unzip [WinMetadata.zip](https://archive.org/download/win-metadata/WinMetadata.zip)

to $HOME/.Affinitywine/drive_c/windows/system32

## Running Affinity Setup and Installing Photo/Designer/Publisher

Press launch and the setup should work

Once its done installing right click to affinity on heroic and go to the details tab

Click on the 3 dots (located on the right top corner)

Edit 

```
App/Game
```

Next Change the executable to 

```
drive_c/Program Files/Affinity/Photo 2/Photo.exe
```
```
drive_c/Program Files/Affinity/Designer 2/Designer.exe
```

```
drive_c/Program Files/Affinity/Publisher 2/Publisher.exe
```

Click finish & launch it.

## Trouble Shooting

(Change the settings in the wine tab if it doesn't work or if you have gpu glitches (it should work fine tho) )

# Optional wine dark theme 🍷
1.Download this file https://raw.githubusercontent.com/Twig6943/AffinityOnLinux/main/wine-dark-theme.reg

2.Right click to your affinity app and go to settings

3.Click to winetricks

4.Click to OPEN WINETRICKS GUI

5.Select default prefix

6.Run regedit

7.Registry>Import registry file

8.Pick the file you've downloaded earlier (wine-dark-theme.reg)

9.You should now have dark theme working

### Special Thanks

[Ardishco](https://github.com/raidenovich)

```
Deviaze

Kemal

Jacazimbo <3

Kharoon

Jediclank134
```
