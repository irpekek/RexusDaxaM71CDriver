# Driver for Rexus Daxa M71 Classic

This is an open-source driver for changing RGB color Rexus Daxa M71 Classic keyboard targeted for linux systems.

## Requirements

This project is written using Python 3

This module is required to run the application:

- `pyusb`

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install module

```bash
pip install pyusb
```

## Usage

Clone this repo using git

```bash
git clone https://github.com/irpekek/RexusDaxaM71CDriver.git
```

Run the file called rexus.py using python

```bash
python rexus.py
```

## Note

There may be bugs or missing features, The script requires root access (sudo) to write/read from the USB device The author takes no responsibility for anything that may go wrong!

You can running this script without sudo by adding UDEV Rules ([see here](https://wiki.archlinux.org/index.php/udev#Accessing_firmware_programmers_and_USB_virtual_comm_devices))

This should be able to setup a udev rule for the device, as to not require root access like so:

```bash
echo "SUBSYSTEMS==\"usb\", ATTRS{idVendor}==\"05ac\", ATTRS{idProduct}==\"024f\", GROUP=\"users\", MODE=\"0660\"" | sudo tee /etc/udev/rules.d/50-rexuskeyboard.rules
```

This requires your system to have a group called users and your current user also needs to be added to the group. You could also modify the above command to add the permission to a group you're already a part of by modifiying "users" to the appropriate group name.

If you want to go the recommended route and dont have a group called users or are not added to the group then run:

```bash
sudo groupadd users
sudo usermod -a -G users your_user_name
```

After which you'll need to restart your device

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Badges

![badmath](https://img.shields.io/github/languages/top/irpekek/RexusDaxaM71CDriver)
