First, make sure your system is up to date. Run
```sh
sudo pacman -Syu
```

Next, install all dependencies required for Grapejuice.
```sh
sudo pacman -S git python-pip python-setuptools python-virtualenv cairo gtk3 gobject-introspection desktop-file-utils xdg-utils xdg-user-dirs gtk-update-icon-cache shared-mime-info mesa-utils
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
