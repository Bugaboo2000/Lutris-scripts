title: Install Grapejuice from source
---

**Table of Contents**

[TOC]

## Preamble

💻 All commands in this guide should be run in a terminal emulator using a regular user account that has access to `su`
or `sudo`. If you are running a fully fledged desktop environment, you can find a terminal emulator in your applications
menu.

---

💻 Grapejuice assumes your desktop is configured properly.


## Specific device notes

### SteamOS 3.0

Before you begin, if you are using SteamOS 3.0, you will need to run `sudo steamos-readonly disable` before proceeding.

### Android

Android is in a seperate guide: [Install Grapejuice on Android](Android)

## Installing Grapejuice dependencies

ℹ️ Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the
following commands in a terminal emulator for your specific distribution:


Debian / Ubuntu / Pop!_OS and its derivatives:
```sh
sudo apt install -y gettext git python3-pip python3-setuptools python3-wheel python3-dev virtualenv pkg-config mesa-utils libcairo2-dev gtk-update-icon-cache desktop-file-utils xdg-utils libgirepository1.0-dev gir1.2-gtk-3.0 gnutls-bin:i386
```

Arch / Manjaro and its derivatives:
```sh
sudo pacman -S git python-pip python-virtualenv cairo gtk3 gobject-introspection desktop-file-utils xdg-utils xdg-user-dirs gtk-update-icon-cache shared-mime-info mesa-utils
```

Fedora:
```sh
sudo dnf install gettext git python3-devel python3-pip python3-virtualenv cairo-devel gobject-introspection-devel cairo-gobject-devel make xdg-utils glx-utils
```

Gentoo:
```sh
sudo emerge --ask sys-devel/gettext dev-vcs/git dev-python/pip dev-python/virtualenv x11-libs/cairo x11-libs/gtk+ dev-libs/gobject-introspection dev-util/desktop-file-utils x11-misc/xdg-utils x11-misc/xdg-user-dirs dev-util/gtk-update-icon-cache x11-misc/shared-mime-info x11-apps/mesa-progs
```

OpenSUSE:
```sh
sudo zypper install gettext-runtime git python3-devel python3-pip python3-virtualenv cairo-devel gobject-introspection-devel make xdg-utils gtk3-devel python3-gobject-Gdk
```

Solus:
```sh
sudo eopkg it -c system.devel
sudo eopkg install gettext git python3-devel virtualenv libcairo-devel xdg-utils
```

FreeBSD:
```sh
sudo pkg install gettext git py39-pip py39-virtualenv cairo gtk3 gobject-introspection desktop-file-utils xdg-utils xdg-user-dirs gtk-update-icon-cache shared-mime-info python38
```

Void Linux:
```sh
sudo xbps-install -S gettext python3 python3-pip python3-wheel python3-virtualenv python3-psutil python3-setuptools python3-cairo python3-gobject cairo-devel desktop-file-utils xdg-user-dirs xdg-utils gtk-update-icon-cache shared-mime-info pkg-config gobject-introspection
```

Slackware:
```sh
sudo slackpkg install gettext gettext-tools python3 python-pip virtualenv cairo pycairo gobject-introspection make xdg-utils p7zip
```

## Installing Grapejuice

First, you have to acquire a copy of the source code. This is easily done by cloning the git repository.

```sh
git clone --depth=1 https://gitlab.com/brinkervii/grapejuice.git /tmp/grapejuice
```

After the git clone command is finished, Grapejuice can be installed.

```sh
cd /tmp/grapejuice
./install.py
```

Once Grapejuice has been installed, you can proceed to the section below.

## 🍷 Installing Wine

**You will need to install a patched Wine build for Grapejuice to work correctly.**
See [this guide](Installing-Wine) for instructions on installing a patched Wine build.

## 🤔 Still having issues?

Even after installing Grapejuice and the patched wine version above, you may still have issues (examples: bad performance, Roblox not opening, etc). Usually, you can find the solutions here: [Troubleshooting page](Troubleshooting)

