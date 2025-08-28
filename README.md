# Automatic-OptiFine-Patcher

A cross-platform Python script that **downloads and patches OptiFine** into a standalone mod `.jar` file.  
This allows it to be used with loaders like **Forge/Fabric** in any launcher, such as PrismLauncher.  
The script supports all OptiFine versions available on [optifine.net](https://optifine.net).

---

## Important

For **Minecraft 1.16.5 or later**, we highly recommend using [Sodium](https://modrinth.com/mod/sodium) instead of OptiFine.  
Sodium offers better performance and compatibility with mods.

If you still want OptiFine features, check out [OptiFabric](https://modrinth.com/modpack/optifabric-modpack),   
which combines Sodium and other mods for a more complete OptiFine experience.

---

## Requirements

### Python

You need Python 3 installed.

* **Windows**

  ```
  winget install Python.Python3
  ```
* **Debian/Ubuntu**

  ```
  sudo apt update && sudo apt install python3
  ```
* **Arch Linux**

  ```
  sudo pacman -S python
  ```
* **Fedora/RHEL**

  ```
  sudo dnf install python3
  ```

### Java

Java is required for patching.

* **Windows**

  ```
  winget install EclipseAdoptium.Temurin.17.JRE
  ```
* **Debian/Ubuntu**

  ```
  sudo apt install openjdk-17-jre
  ```
* **Arch Linux**

  ```
  sudo pacman -S jdk17-openjdk
  ```
* **Fedora/RHEL**

  ```
  sudo dnf install java-17-openjdk
  ```

> If installed manually, make sure Java is added to your `PATH`.

---

## Download

Get the latest release from [Codeberg Releases](https://codeberg.org/marvin1099/AutomaticOptifinePatcher/releases/latest).  
Download the `optifine_patcher.py` and place it in an empty folder.

---

## Usage

Run the script from a terminal/command prompt:

```bash
cd PATH/TO/PATCHER
./optifine-patcher.py [options]
```

Check [Examples](#examples) for a jumpstart (section after options)

### Options

| Flag               | Description                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| `-l [MC_VERSION]`  | List available OptiFine versions (optionally filtered by MC version).                          |
| `-d [VERSION]`     | Download and patch OptiFine (`newest` if not specified).                                       |
| `-j /path/to/java` | Use a custom Java executable (default: `java`).                                                |
| `-w DIR`           | Set a custom working directory (relative or absolute).                                         |
| `-n`               | Only include non-preview versions when downloading.                                            |
| `-r`               | Re-download and overwrite files instead of skipping.                                           |
| `-c`               | Clean up (delete) the downloaded OptiFine and client `.jar` files.                             |
| `-m`               | Move the patched mod `.jar` into the working directory and delete the build folder (if empty). |
| `-f`               | Remove the entire folder after a successful `-m` move.                                         |

---

## Examples

### Listing

List all available OptiFine versions:

```bash
./optifine-patcher.py -l
```

List OptiFine releases for Minecraft 1.8.x (eg. 1.8.0, 1.8.8 and 1.8.9):

```bash
./optifine-patcher.py -l 1.8
```

### Downloading and patching

Download and patch the **latest OptiFine** for the newest supported Minecraft version:

```bash
./optifine-patcher.py -d
```

Download and patch a **specific version** (Eg. 1.10.2_HD_U_D8):

```bash
./optifine-patcher.py -d 1.10.2_HD_U_D8
```

  * The patched file will be created inside a versioned subfolder, for example:
    ```
    1.10.2/OptiFine_1.10.2_HD_U_D8-MOD.jar
    ```

Download latest OptiFine for Minecraft 1.9.4:

```bash
./optifine-patcher.py -d 1.9.4
```

Force re-download of OptiFine and client (1.12.2), then clean up:

```bash
./optifine-patcher.py -d 1.12.2 -r -c
```

Download newest 1.14 (1.14.4), patch, and move the result into working dir:

```bash
./optifine-patcher.py -d 1.14 -m -f
```

Download newest 1.13.0 (listed on optifine as 1.13 but means the same thing):

```bash
./optifine-patcher.py -d 1.13.0
```
