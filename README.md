# Simple Mac Restore

**Simple Mac Restore** fixes a broken Apple Silicon Mac (M1, M2, M3, etc.) using a **Linux computer**. It downloads the required system file (IPSW) and communicates with your Mac in **DFU mode** to revive or fully restore it. 

You do **not** need a second Mac, just a Linux machine, a reliable USB cable, and an internet connection.

---

## What It Does

* **Download IPSW:** Grabs the official Apple firmware for your specific Mac model.
* **Revive:** Reflashes the firmware **without erasing** your data. Useful for system corruption.
* **Restore:** **Erases everything** on the Mac for a completely fresh install. **All data is lost.**
* **Custom Tools:** Allows non-Fedora users to use manually compiled restore tools (`idevicerestore`, `usbmuxd`).

---

## Important Warnings

1.  **Data Loss:** "Restore" wipes the machine completely. "Revive" attempts to save data but isn't guaranteed. Back up if possible.
2.  **Linux Support:** The automated setup script is designed for **Fedora**. On Ubuntu, Debian, or Arch, you must use a Fedora Live USB, Docker, or manually build the required dependencies.
3.  **Hardware:** Use a high-quality USB cable connected directly to your computer's port (avoid hubs). 
4.  **Root Access:** Running USB tools requires `sudo` privileges.

---

## Requirements & Dependencies

* **OS:** Linux (Fedora recommended).
* **Software:** Python 3 (with `tkinter` for file dialogs).
* **Dependencies** (Auto-installed on Fedora via setup script): `libimobiledevice`, `idevicerestore`, `usbmuxd`, `simple-term-menu`, `requests`, `tqdm`, `pyusb`.

---

## Quick Start


### 1. Download the repo
Open a terminal and run:
```bash
git clone https://github.com/mrrabyss/SimpleMacRestore
```


### 2. Run Setup (Fedora)
Open a terminal in the project folder and run:
```bash
chmod +x setup.sh SimpleMacRestore.sh
./setup.sh
```
*(If you are not on Fedora, follow the warnings printed by the script to handle dependencies).*

### 3. Enter DFU Mode
Connect your Mac to the Linux PC via USB. Follow Apple’s official instructions for your specific Mac model to enter **DFU mode**.

### 4. Start the App
```bash
./SimpleMacRestore.sh
```
*(Alternatively, activate the `.venv` and run `python3 main.py`).*

### 5. Follow the Menu
Use your arrow keys and Enter to:
1.  **Download IPSW** for your Mac model.
2.  Choose **Revive** (keep data) or **Restore** (wipe data).

---

## File Locations & Troubleshooting

* **Downloads:** IPSW files are saved in the main project folder.
* **Logs:** Saved in the `logs/` folder (enable this in the app Settings).
* **If it fails:** * Verify the Mac is in DFU mode (run `lsusb` to look for an Apple DFU device).
    * Try a different cable or USB port.
    * Ensure the downloaded IPSW perfectly matches your Mac model.
    * Non-Fedora users: ensure your `idevicerestore` and `usbmuxd` binaries are up to date and configured via **Settings → Custom binary dir**.



**Disclaimer:** Firmware restoration is a serious operation. Interrupted restores, incorrect files, or hardware issues can leave a device in an unusable state. **You use this tool at your own risk.** 

## License

Licensed under MIT.

