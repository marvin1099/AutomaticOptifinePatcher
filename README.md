# Automatic-Optifine-Patcher
A cross-platform Python script that patches OptiFine to work as a jar mod file.  
This allows it to be used with mod loaders like Forge/Fabric with any mod launcher, such as PrismLauncher.  
The script supports all OptiFine versions from optifine.net and downloads them fully automaticly.  

## Important
For Minecraft version 1.16.5 or later, we strongly recommend using [Sodium](https://modrinth.com/mod/sodium) instead of OptiFine.  
Sodium provides significantly better performance and compatibility with other mods.

## Requirements

### Python
You need Python installed on your system to run the script.

#### **Windows**
Download Python from the [official website](https://www.python.org/downloads/), or install it using the Windows Package Manager:
```
winget install Python.Python3
```

#### **Linux**
On Linux, install Python using your distribution's package manager:
- **Debian/Ubuntu-based systems:**
  ```
  sudo apt update && sudo apt install python3
  ```
- **Arch-based systems:**
  ```
  sudo pacman -S python
  ```
- **Fedora/RHEL-based systems:**
  ```
  sudo dnf install python3
  ```
  
### Java
Java is required for the patching process. Install the latest stable version of Java for your system using the appropriate method below.

#### **Windows**  
Install Java using the Windows Package Manager:  
```
winget install EclipseAdoptium.Temurin.17.JRE
```  
This will install Java 17, ensuring compatibility.

Alternatively, download Java manually from [OpenLogic](https://www.openlogic.com/openjdk-downloads) or another provider. If installed manually, add Java to your PATH environment variable by following this [guide](https://confluence.atlassian.com/doc/setting-the-java_home-variable-in-windows-8895.html).

#### **Linux**  
Install Java using your distribution's package manager to get the latest supported version:
- **Debian/Ubuntu-based systems:**
  ```
  sudo apt install openjdk-17-jre
  ```
- **Arch-based systems:**
  ```
  sudo pacman -S jdk17-openjdk
  ```
- **Fedora/RHEL-based systems:**
  ```
  sudo dnf install java-17-openjdk
  ```

For consistency, all package managers install Java 17 in this guide. If a newer version is preferred, replace `17` with the desired version number.  

For manual installation, download Java from [OpenLogic](https://www.openlogic.com/openjdk-downloads) and add it to your system's PATH.

## Download
Download the patcher script from [here](https://codeberg.org/marvin1099/Automatic-Optifine-Patcher/src/branch/main/optifine_patcher.py).  
Click the download button at the top-right and save the file in an empty folder.

## Usage
1. Open a terminal (or Command Prompt on Windows) and navigate to the folder containing `optifine_patcher.py`:
   ```
   cd "PATH/TO/PYTHON/FILE"
   ```
   Replace `PATH/TO/PYTHON/FILE` with the path to the folder containing the script.

2. List available OptiFine versions for a specific Minecraft version (e.g., `1.9`):
   ```
   ./optifine-patcher.py -l 1.9
   ```

3. Use the version from the results (e.g., `1.9.4`) to download and patch:
   ```
   ./optifine-patcher.py -d 1.9.4
   ```

4. The patched OptiFine file will be saved as:
   ```
   PATH/TO/PYTHON/FILE/$VERSION/optifine-$VERSION-MOD.jar
   ```
   Replace `$VERSION` with the version you downloaded (e.g., `1.9.4`).

## Custom Java Path
If Java is not added to your PATH environment variable, specify the Java path manually:
```
./optifine-patcher.py -j "/PATH/TO/JAVA" -d 1.9.4
```
Replace `/PATH/TO/JAVA` with the full path to your Java binary (e.g., `java` or `java.exe`).
