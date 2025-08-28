# Automatic-OptiFine-Patcher

A cross-platform Python script that **downloads and patches OptiFine** into a standalone mod `.jar` file.
This allows it to be used with loaders like **Forge/Fabric** in any launcher, such as PrismLauncher.
The script supports all OptiFine versions available on [optifine.net](https://optifine.net).

---

## Important

For **Minecraft 1.16.5 or later**, we highly recommend using [Sodium](https://modrinth.com/mod/sodium) instead of OptiFine.
Sodium offers better performance and compatibility with mods.

If you still want OptiFine features, check out [OptiFabric](https://modrinth.com/modpack/optifabric-modpack), which combines Sodium and OptiFine for a more stable experience.

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
Download the `optifine_patcher.py` (or `new_patcher.py`) and place it in an empty folder.

---

## Usage

Run the script from a terminal/command prompt:

```bash
cd PATH/TO/PATCHER
./optifine-patcher.py [options]
```

### Listing Versions

* List all available OptiFine versions:

  ```bash
  ./optifine-patcher.py -l
  ```
* List versions for a specific Minecraft version (e.g. `1.16`):

  ```bash
  ./optifine-patcher.py -l 1.16
  ```

### Downloading & Patching

* Download and patch the **latest OptiFine** for the newest supported Minecraft version:

  ```bash
  ./optifine-patcher.py -d
  ```
* Download and patch a **specific version**:

  ```bash
  ./optifine-patcher.py -d 1.16.5_HD_U_G8
  ```

The patched file will be created inside a versioned subfolder, for example:

```
1.16.5/OptiFine_1.16.5_HD_U_G8-MOD.jar
```

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

Download latest OptiFine for Minecraft 1.12.2:

```bash
./optifine-patcher.py -d 1.12.2
```

List only OptiFine releases for Minecraft 1.8:

```bash
./optifine-patcher.py -l 1.8
```

Force re-download of OptiFine and client, then clean up:

```bash
./optifine-patcher.py -d 1.16.5 -r -c
```

Download, patch, and move the result into working dir:

```bash
./optifine-patcher.py -d 1.19.2 -m -f
```
