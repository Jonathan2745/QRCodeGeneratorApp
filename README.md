# vCard QR Code Generator App

A desktop QR code generator built with **Python 3.14**, **PySide6**, `qrcode`, and Pillow.

This app provides a simple GUI for generating QR codes in vCard format from user-provided text, URLs, contact details, payment strings, or other QR-compatible content.

## Features

* Generate QR codes from custom text input
* Save generated QR codes as image files
* Desktop GUI built with PySide6 / Qt
* Configurable default output path and QR styling through `.env`
* Clean Python project structure using `pyproject.toml`
* Development tools included for testing, linting, and formatting

## Tech Stack

* Python 3.14
* PySide6
* qrcode
* Pillow
* python-dotenv
* pytest
* pytest-qt
* ruff

## Project Structure

```text
QRCodeGeneratorApp/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── src/
│   └── qrgenerator/
│       ├── __init__.py
│       ├── main.py
│       ├── main_window.py
│       ├── config.py
│       └── qr_service.py
└── tests/
    └── test_qr_service.py
```

## Requirements

* Python 3.14
* pip
* Windows, macOS, or Linux

This project is currently developed using a local Python virtual environment.

## Setup

### 1. Clone or open the project folder

```powershell
cd "C:\path\to\QRCodeGeneratorApp"
```

For macOS or Linux:

```bash
cd "/path/to/QRCodeGeneratorApp"
```

### 2. Create a virtual environment

On Windows:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal should show `(.venv)`.

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install the project dependencies

Install the app in editable development mode:

```bash
pip install -e ".[dev]"
```

This installs the main app dependencies and development tools.

Main dependencies:

```text
PySide6
qrcode[pil]
Pillow
python-dotenv
```

Development dependencies:

```text
pytest
pytest-qt
ruff
```

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
APP_NAME=QR Generator
DEFAULT_OUTPUT_DIR=output
DEFAULT_QR_FILENAME=qr_code.png

QR_BOX_SIZE=10
QR_BORDER=4
QR_FILL_COLOR=black
QR_BACK_COLOR=white

LOG_LEVEL=INFO
```

A `.env.example` file should also be included in the repository so other users know which settings are required.

The `.env` file is used for local configuration and should not be committed to Git.

## Running the App

After installing the project, run:

```bash
qrgenerator
```

Alternatively, run the module directly:

```bash
python -m qrgenerator.main
```

## Basic Usage

1. Open the app.
2. Enter the content you want to encode into a QR code.
3. Click the generate button.
4. The generated QR code will be saved to the configured output directory.

By default, the output file is saved as:

```text
output/qr_code.png
```

## Testing Imports

To verify that all required packages are installed correctly:

```bash
python -c "import qrcode; from PIL import Image; from PySide6 import QtWidgets; print('All imports OK')"
```

Expected output:

```text
All imports OK
```

## Running Tests

Run all tests:

```bash
pytest
```

Example test coverage should include:

* QR code generation
* Output file creation
* Empty input validation
* Configuration loading

## Formatting and Linting

Format the code:

```bash
ruff format .
```

Check for linting issues:

```bash
ruff check .
```

Fix automatically fixable linting issues:

```bash
ruff check . --fix
```

## Packaging the App

For Windows, the app can be packaged into an executable using PyInstaller.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the app:

```bash
pyinstaller --name QRGenerator --windowed src\qrgenerator\main.py
```

The output will be created in:

```text
dist/QRGenerator/
```

For macOS, the app can be packaged later as a `.app` bundle.

## Common Issues

### `ModuleNotFoundError: No module named 'qrcode'`

Make sure your virtual environment is activated, then reinstall dependencies:

```bash
pip install -e ".[dev]"
```

### `ModuleNotFoundError: No module named 'PIL'`

Do not install `pil`.

Use Pillow instead:

```bash
pip install Pillow
```

Or reinstall all project dependencies:

```bash
pip install -e ".[dev]"
```

### PowerShell blocks virtual environment activation

If Windows PowerShell prevents activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Hatch cannot find the package folder

If `pip install -e ".[dev]"` fails with an error saying it cannot determine which files to ship, make sure the project contains:

```text
src/qrgenerator/__init__.py
```

Also ensure `pyproject.toml` includes:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/qrgenerator"]
```


## License

This project is for internal or personal use unless a license is added.
