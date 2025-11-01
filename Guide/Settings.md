# Settings

Affinity apps sometimes tend not to save settings properly. There are two methods of fixing this. Given a `wineprefix` of `drive_c/users/$USERNAME/AppData/Roaming/Affinity/`:

1. Clone this repository and copy the files from [./Auxiliary/](../Auxiliary/Settings) to their respective paths inside the `wineprefix`.
2. Locate the settings folders on a windows machine and paste them into the
   corresponding locations in the `wineprefix`.

## Method 1

This method is tested and working for the recommended [Lutris/EW](../Guides/Lutris/Guide.md) install. 

Clone the repository and move into the source directory:
```sh
git clone git@github.com:seapear/AffinityOnLinux.git
cd AffinityOnLinux/Auxiliary/Settings/
```

Execute the following code for each app, each time replacing `$APP` with the name of the
target Affinity application and `$USERNAME` with the name of the user. 

```sh
mv $APP/2.0/Settings drive_c/users/$USERNAME/AppData/Roaming/Affinity/
```

## Method 2

Copy the respective settings folders from `C:\\\users\$USERNAME\AppData\Roaming\Affinity\$APP\$VERSION\Settings\` on windows into the corresponding directory inside the `wineprefix`.

For example:

```sh
C:\\\users\$USERNAME\AppData\Roaming\Affinity\Designer\2.0\Settings\ -> drive_c/users/$USERNAME/AppData/Roaming/Affinity/Designer/2.0/

C:\\\users\$USERNAME\AppData\Roaming\Affinity\Photo\2.0\Settings\ -> drive_c/users/$USERNAME/AppData/Roaming/Affinity/Photo/2.0/

C:\\\users\$USERNAME\AppData\Roaming\Affinity\Publisher\2.0\Settings\ -> drive_c/users/$USERNAME/AppData/Roaming/Affinity/Designer/2.0/
```

## Editing The Settings Files

The settings files use the `.xml` format and can be modified using a text editor.
