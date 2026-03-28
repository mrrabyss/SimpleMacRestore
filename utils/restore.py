import os
import select
import subprocess
import time
import usb.core
import usb.util

DFU_KEYWORD = "Apple Mobile Device (DFU)"
APPLE_VID = 0x05AC

def find_apple_dfu():
    try:
        devices = usb.core.find(find_all=True)
    except (usb.core.USBError, ValueError, OSError) as e:
        # Handle USB backend errors, permission issues, etc.
        return False

    if devices is None:
        return False

    for dev in devices:
        if dev.idVendor != APPLE_VID:
            continue  

        try:
            vendor_str = usb.util.get_string(dev, dev.iManufacturer)
            product_str = usb.util.get_string(dev, dev.iProduct)
        except usb.core.USBError:
            continue 

        if vendor_str == "Apple Inc." and product_str == DFU_KEYWORD:
            return True

    return False

def wait_for_dfu():
    try:
        while not find_apple_dfu():
            print("Waiting for device in DFU mode..........")
            time.sleep(1)
        print("Device in DFU mode detected!")
        return
    except KeyboardInterrupt:
        exit()

def restore(ipsw_path: str | None, logfile: str | None, erase: bool = False, custom_bin_dir: str = ""):
    args = []
    if erase == True:
        print("""
                                                    ###################################################
                                                        CAUTION! YOU ARE ABOUT TO ERASE YOUR DEVICE!  
                                                    ###################################################
    You are about to perform a full restore of your Apple Silicon Mac.
	-	All data on the target device will be ERASED PERMANENTLY.
	-	This operation CANNOT BE UNDONE once the restore begins.
	-	Interrupting the restore (cable disconnect, power loss, wrong firmware, etc.) can cause device corruption or require another DFU restore.
	-	The developers of SimpleMacRestore, as well as the maintainers of idevicerestore and usbmuxd, are NOT responsible for data loss, corruption, or hardware issues.
	-	Proceed entirely at your own risk..""")
        confirmation = input("If you aknowledge the risks, type YES to perform RESTORE,if you want to CANCEL, press enter: ")
        if confirmation != "YES": 
            return False
        else:
            args.append("-e")
    args.append(ipsw_path)
    idevicerestore_path = os.path.join(custom_bin_dir, "idevicerestore") if custom_bin_dir else "idevicerestore"
    args.insert(0, idevicerestore_path)
    idevicerestore = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1 
    )
    saved_output = []
    input_sent = False
    while True:
    # Wait until stdout has something to read
        rlist, _, _ = select.select([idevicerestore.stdout], [], [], 1)
        
        if idevicerestore.stdout in rlist:
            line = idevicerestore.stdout.readline()
            if not line:  # EOF
                break
            # Print live
            print(line, end="")
            # log saving
            saved_output.append(line)
            
            # Detect process is ready for input: send it once
            if not input_sent:
                # any output means process is ready for stdin
                try:
                    idevicerestore.stdin.write("YES\n")  
                    idevicerestore.stdin.flush()
                    idevicerestore.stdin.close()  # no more input
                    input_sent = True
                except BrokenPipeError:
                    pass
        # check if process exited
        if idevicerestore.poll() is not None:
            break
    if logfile:
        parts = logfile.split("_")
        timestamp = parts[1] if len(parts) > 1 else str(int(time.time()))
        content = f"idevicerestore logs, unix time: {timestamp}\n"
        for line in saved_output:
            content += line
        with open(logfile, "w", encoding="utf-8") as f:
            f.write(content)
    print(
        f"All done! The logs have been saved to: {logfile if logfile else '(logs are disabled)'}\n"
        "Your device should boot into recovery menu or setup screen \n"
        "If you seen any errors or your mac still does not boot, you should probably check the logs and try again. "
        "Common fixes can be found in README.md file."
    )
    return True