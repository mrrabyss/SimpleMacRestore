#!/bin/bash
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" = "fedora" ]; then
        sudo dnf update
        sudo dnf install libimobiledevice idevicerestore usbmuxd
        python3 -m venv .venv
        source .venv/bin/activate
        pip3 install -r requirements.txt
        echo "Setup is done! Run 'python3 main.py' "
    else
        echo "################################################################################## CAUTION ######################################################################################################################"
        echo "You are not running Fedora, so this script can't install latest crucial libraries."
        echo "You either have to use Fedora Live CD, but if you don't want to use it, you can install docker(see: https://docs.docker.com/engine/install/) and then run sudo docker run --rm --privileged --net=host -v /dev/bus/usb:/dev/bus/usb -v /run:/run -v .:/mnt -ti fedora:rawhide"
        echo "Or, compile latest idevicerestore, libimobiledevice, usbmuxd binaries yourself and place them into one folder, then do manual setup of this tool(see: https://github.com/mrrabyss/SimpleMacRestore/?tab=readme-ov-file#manual-setup)"
        echo "After you've done all that, create a new python venv and activate it via: python3 -m venv .venv; source .venv/bin/activate commands. Then run pip3 install -r requirements.txt "
        echo "################################################################################## CAUTION ######################################################################################################################"
    fi
fi
