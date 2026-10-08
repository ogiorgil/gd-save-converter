# Geometry Dash Save Converter

Convert Geometry Dash save files between **Windows and macOS**.

Supports both directions:

- **Windows → macOS**
- **macOS → Windows**

It converts the two local save files used by Geometry Dash:

- `CCGameManager.dat` — player progress, icons, settings, and statistics
- `CCLocalLevels.dat` — locally created levels

The converter does not connect to Geometry Dash or upload files.

## Before you start

Option 1: Point your friendly local coding agent to this project and let it do its thing.
Option 2:
1. Close Geometry Dash.
2. Back up the original save files.
3. Copy `CCGameManager.dat` and `CCLocalLevels.dat` into the project folder.
4. Install Python 3.9 or newer.

### Windows dependency

Install PyCryptodome from the project folder:

```bat
python -m pip install -r requirements.txt
```

### macOS dependency

Check whether OpenSSL is available:

```sh
openssl version
```

If OpenSSL is unavailable, install PyCryptodome from the project folder:

```sh
python3 -m pip install -r requirements.txt
```

## Windows → macOS

### 1. Find the Windows save files

On Windows, Geometry Dash usually stores its saves in:

```text
C:\Users\<your-Windows-username>\AppData\Local\GeometryDash\
```

You need these files:

```text
CCGameManager.dat
CCLocalLevels.dat
```

Copy both files into the project folder alongside `gd_save_converter.py`.

### 2. Open Terminal on the Mac

Open **Terminal** and change to the project folder:

```sh
cd "/path/to/gd-save-converter"
```

### 3. Convert both files

Run these commands in the project folder:

```sh
python3 gd_save_converter.py --from windows CCGameManager.dat

python3 gd_save_converter.py --from windows CCLocalLevels.dat
```

Each file is converted in place and a `.backup` copy is created.

### 4. Put the converted files in the Mac save folder

The Mac Geometry Dash save folder is:

```text
~/Library/Application Support/GeometryDash/
```

In Finder, press **Command + Shift + G**, enter that path, and press Enter.
Back up the existing files, then copy the converted files there. Rename them:

```text
CCGameManager.dat
CCLocalLevels.dat
```

## macOS → Windows

### 1. Find the Mac save files

The Mac Geometry Dash save folder is:

```text
~/Library/Application Support/GeometryDash/
```

In Finder, press **Command + Shift + G**, enter that path, and press Enter.
Copy both files to the Windows computer and into the project folder:

```text
CCGameManager.dat
CCLocalLevels.dat
```

### 2. Open a terminal

Open **PowerShell** or **Command Prompt** and change to the project folder:

```bat
cd "C:\path\to\gd-save-converter"
```

### 3. Convert both files

Run these commands in the project folder:

```bat
python gd_save_converter.py --from macos CCGameManager.dat
python gd_save_converter.py --from macos CCLocalLevels.dat
```

Each file is converted in place and a `.backup` copy is created.

### 4. Put the converted files in the Windows save folder

On Windows, Geometry Dash usually stores its saves in:

```text
C:\Users\<your-Windows-username>\AppData\Local\GeometryDash\
```

Back up the existing files, then copy the converted files there. Rename them:

```text
CCGameManager.dat
CCLocalLevels.dat
```

The converter will not replace an existing `.backup` file. Remove it before
converting again.

## Safety

- Close Geometry Dash before converting or replacing files.
- Back up the original files.
- Save files can contain account and login-session data. Do not publish them.

## Formats

The save data is compatible, but the file encoding differs:

- **Windows:** gzip → URL-safe Base64 → XOR with `0x0B`
- **macOS:** AES-256-ECB

The converter preserves the save data and changes only its file format.
Encryption details: [GD Docs](https://wyliemaster.github.io/gddocs/#/topics/localfiles_encrypt_decrypt).
