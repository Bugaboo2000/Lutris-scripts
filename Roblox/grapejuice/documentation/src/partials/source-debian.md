First, make sure your system is fully up to date. Run the following command:
```sh
sudo apt update && apt upgrade
```

Now make sure all dependencies are installed. Run the following command:
```sh
sudo apt install -y gettext git python3-pip python3-setuptools python3-wheel python3-dev virtualenv pkg-config mesa-utils libcairo2-dev gtk-update-icon-cache desktop-file-utils xdg-utils libgirepository1.0-dev gir1.2-gtk-3.0 gnutls-bin:i386
```

To install Grapejuice from source, you actually need the source first. Download the source code by running this command:
```sh
git clone --depth=1 https://gitlab.com/brinkervii/grapejuice.git /tmp/grapejuice
```

When the git clone command has finished, you can actually install Grapejuice by running these commands:
```sh
cd /tmp/grapejuice
./install.py
```