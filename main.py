from simple_term_menu import TerminalMenu
from tkinter.filedialog import askopenfilename, askdirectory
import sys
import subprocess, signal
import os
from utils.fetch import get_firmwares_for_mac, get_ipsw_url, download_ipsw, build_macs_list
from utils.restore import restore, wait_for_dfu
import time


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def print_banner():
    banner = """
 ____  _                 _      __  __            ____           _                 
/ ___|(_)_ __ ___  _ __ | | ___|  \\/  | __ _  ___|  _ \\ ___  ___| |_ ___  _ __ ___ 
\\___ \\| | '_ ` _ \\| '_ \\| |/ _ \\ |\\/| |/ _` |/ __| |_) / _ \\/ __| __/ _ \\| '__/ _ \\
 ___) | | | | | | | |_) | |  __/ |  | | (_| | (__|  _ <  __/\\__ \\ || (_) | | |  __/
|____/|_|_| |_| |_| .__/|_|\\___|_|  |_|\\__,_|\\___|_| \\_\\___||___/\\__\\___/|_|  \\___|
                  |_|                                                                                                                                                                                     
"""
    os.system("clear")
    print(banner)

save_logs = True
custom_bin_dir = ""


def restoring_menu():
    # ipsw selector
    print_banner()
    ipsw_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".ipsw")]
    ipsw_options = ipsw_files + ["Custom path", "Select from file manager", "<- Back to main menu"]
    ipsw_menu = TerminalMenu(ipsw_options, title="Choose an iPSW file")

    path = None
    while path is None:
        ipsw_choice = ipsw_menu.show()
        custom_idx = len(ipsw_files)
        file_picker_idx = custom_idx + 1
        back_idx = custom_idx + 2

        if ipsw_choice is None or ipsw_choice == back_idx:
            return
        if ipsw_choice < custom_idx:
            path = os.path.join(BASE_DIR, ipsw_files[ipsw_choice])
        elif ipsw_choice == custom_idx:
            entered = input("Please enter a path to an iPSW file: ").strip()
            if os.path.exists(entered):
                path = entered
            else:
                input("File does not exist. Press ENTER to try again...")
        elif ipsw_choice == file_picker_idx:
            picked = askopenfilename(filetypes=(("iPSW Files", "*.ipsw"), ("All files", "*.*")))
            if picked:
                path = picked
            else:
                input("No file selected. Press ENTER to try again...")
    # select if user wants to revive or restore
    print_banner()
    ropt = ["Revive", "Restore", "<- Back to main menu"]
    r_menu = TerminalMenu(ropt, title="Choose if you want to revive or restore your Mac. If you dont know what to choose, please go to the Help option in the main menu.")
    r_choice = r_menu.show()
    if r_choice == 2: main_menu()
    else:
        erase = True if r_choice == 1 else False
        logfile = None
        if save_logs == True:
            if not os.path.exists(f"{BASE_DIR}/logs"): os.mkdir("logs")
            logfile = f"{BASE_DIR}/logs/log_{int(time.time())}_.txt"
            open(logfile, "x").close()
        try:
            usbmuxd_path = os.path.join(custom_bin_dir, "usbmuxd") if custom_bin_dir else "usbmuxd"
            usbmuxd = subprocess.Popen([usbmuxd_path, "-f", "-U", "root", "-v"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,start_new_session=True)
            usbmuxd_pid = usbmuxd.pid # have to save this in order to be able to kill this at the end
            # wait for dfu mode
            while True:
                print("Waiting for device to enter DFU mode......")
                lsusb_output = subprocess.check_output(["lsusb"], text=True)
                if "Apple" in lsusb_output and "DFU" in lsusb_output:
                    break
                time.sleep(1)
            #begin restoring
            wait_for_dfu()
            restore(path,logfile,erase,custom_bin_dir)
            os.killpg(usbmuxd_pid, signal.SIGTERM)
            input("Press ENTER to continue.......")
            return
        except FileNotFoundError: 
            print("Please install all dependencies or specify a correct binary directory!!")
            input("Press ENTER to continue.......")
            return
        except Exception as e:
            print(f"An error occured during the {"revive" if not erase else "restore"} process.\n{str(e)}\n{"Logs have been saved" if save_logs else ""}")
            if save_logs: 
                with open(logfile, "a") as file:
                    file.write(str(e))
            input("Press ENTER to continue.......")
            return
def settings_menu():
    global save_logs, custom_bin_dir
    while True:
        print_banner()
        bin_dir_label = custom_bin_dir if custom_bin_dir else "Default (PATH)"
        options = [
            f"Save logs: {'Enabled' if save_logs else 'Disabled'}",
            f"Custom binary dir: {bin_dir_label}",
            "<- Back to main menu"
        ]
        settings = TerminalMenu(options, title="Settings", exit_on_shortcut=True)
        choice = settings.show()
        if choice is None or choice == 2:
            return
        if choice == 0:
            save_logs = not save_logs
            continue
        if choice == 1:
            bin_options = [
                "Pick directory",
                "Enter path manually",
                "Use default (clear)",
                "<- Back"
            ]
            bin_menu = TerminalMenu(bin_options, title="Select binaries directory")
            bin_choice = bin_menu.show()
            if bin_choice is None or bin_choice == 3:
                continue
            if bin_choice == 0:
                picked = askdirectory(title="Choose directory with binaries")
                if picked and os.path.isdir(picked):
                    custom_bin_dir = picked
                else:
                    input("Invalid directory. Press ENTER to continue...")
            elif bin_choice == 1:
                entered = input("Enter absolute path to directory with binaries: ").strip()
                if entered and os.path.isdir(entered):
                    custom_bin_dir = entered
                else:
                    input("Directory does not exist. Press ENTER to continue...")
            elif bin_choice == 2:
                custom_bin_dir = ""
            continue
def ipsw_downloader_menu():
    # model selector
    print_banner()
    model_options = ["<- Back to menu"]
    model_to_id = {} # its used to get mac ids(e.g Mac17,2)
    mac_list = build_macs_list()
    for mac in mac_list:
        model_options.append(mac.get("name"))
        model_to_id[mac.get("name")] = mac.get("identifier")
    model_menu = TerminalMenu(model_options, title="Choose your Mac:", exit_on_shortcut=True)
    model_choice = model_menu.show()
    if model_choice == 0: main_menu()
    else:
        # os selector
        print_banner()
        macid = model_to_id[model_options[model_choice]]
        firmwares_list = get_firmwares_for_mac(macid)
        firmware_options = []
        version_to_build_num = {} # this is used for verison builds
        for firmware in firmwares_list:
            firmware_options.append(firmware.get("version"))
            version_to_build_num.update({firmware.get("version"): firmware.get("buildid")})
        firmware_menu = TerminalMenu(firmware_options, title="Choose version that you want to download:",exit_on_shortcut=True)
        firmware_choice = firmware_menu.show()
        # downloading 
        url = get_ipsw_url(firmwares_list, version_to_build_num[firmware_options[firmware_choice]])
        download_ipsw(url, BASE_DIR)
        input("Press ENTER to continue......")
        main_menu()

def main_menu():
    # basic main menu
    while True:
        try:
            print_banner()
            options = ["Download iPSW", "Revive/Restore", "Help", "Settings", "Exit"]
            menu = TerminalMenu(options, title="Choose options:")
            choice = menu.show()

            if choice == 0:
                ipsw_downloader_menu()
            elif choice == 1:
                restoring_menu()
            elif choice == 2:
                input(f"Please read the {os.path.join(BASE_DIR, "README.md")} file for any assistanse.\nPress ENTER to go to the main menu.....")
            elif choice == 3:
                settings_menu()
            elif choice == 4 or choice is None:
                sys.exit()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__": main_menu()