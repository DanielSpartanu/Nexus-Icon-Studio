[README.md](https://github.com/user-attachments/files/35058714/README.md)
# 🎨 Nexus Icon & EXE Builder Studio

A lightweight, dark-themed Windows utility that turns any image into a multi-resolution Windows icon (`.ico`) and packages Python scripts (`.py`) into standalone `.exe` programs with a single click.

---

## 🚀 Option 1: Quick Start (Standalone `.EXE` — Recommended)

1. Go to the **[Releases](../../releases)** section on the right and download **`icon_studio.exe`**.
2. Double-click **`icon_studio.exe`** to open the app—no installation required to generate `.ico` icons.
3. *(Note: To use Tab 2 to compile `.py` files into `.exe`, Python and `pyinstaller` must be installed on your PC. If Windows SmartScreen appears on first launch, click **More info → Run anyway**).*

### How to Use
- **Tab 1 — Multi-Res `.ICO` Generator:** Select any `.png`, `.jpg`, `.jpeg`, or `.webp` image, keep **1:1 Auto-Crop** checked for a distortion-free square icon, and click **Generate**. Icons (`16px` up to `256px`) are saved automatically to `Downloads\Nexus_Icons` and pre-loaded into Tab 2.
- **Tab 2 — Python to `.EXE` Compiler:** Choose your `.py` script, pick an `.ico` icon, select **Hide black console** or **Administrator privileges** if needed, and click **Compile to .EXE Now**. Temporary `build/` and `.spec` folders are cleaned up automatically.

---

## 🛠️ Option 2: For Developers (Run or Customize `icon_studio.py`)

If you want to inspect, modify, or run the Python source directly:

1. Make sure you have **Python 3.8+** installed.
2. Install the required dependencies (`pillow` and `pyinstaller`):
   ```bash
   pip install pillow pyinstaller
   ```
3. Run the application:
   ```bash
   python icon_studio.py
   ```

---

## ☕ Support the Project

If you find this tool useful and want to support future free Windows utilities, feel free to buy me a coffee via PayPal:

👉 **[paypal.me/danielspartanboss](https://paypal.me)**
