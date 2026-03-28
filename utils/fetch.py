import requests
import json
import tqdm
import os


def build_macs_list():
    r = requests.get("https://api.ipsw.me/v4/devices")
    response = r.text
    json_response: list[dict[str]] = json.loads(response)
    macs = []
    for device in json_response:
        if device.get("identifier").startswith("Mac"):
            macs.append(device)
    return macs
def get_firmwares_for_mac(macid: str):
    r = requests.get(f"https://api.ipsw.me/v4/device/{macid}?type=ipsw")
    response = r.text
    json_response: dict = json.loads(response)
    return json_response.get("firmwares")
def get_ipsw_url(firmwares: list[dict], buildid: str):
    for firmware in firmwares:
        if firmware.get("buildid") == buildid:
            return firmware.get("url")

def download_ipsw(url: str, save_to_folder: str):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    filename =  url.split("/")[-1]
    print(f"Beginning to download {filename}\n")
    with tqdm.tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
        with open(os.path.join(save_to_folder,filename), "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
    print(f"Download complete! The iPSW is saved in: {os.path.join(save_to_folder,filename)}\n")
    