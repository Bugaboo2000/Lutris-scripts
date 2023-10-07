title: Install Grapejuice from package
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

Before you begin, if you are using SteamOS 3.0, you will need to run `sudo steamos-readonly disable`.

### Android

Android is in a seperate guide: [Install Grapejuice on Android](Android)

## Installing Grapejuice

### Flatpak
If you prefer flatpak for your packages, you could install the grapejuice package.

See [Installing-from-flatpak](Installing-from-flatpak)

### NixOS
```sh
nix-env -iA nixpkgs.grapejuice
```
Alternatively, add to `environment.systemPackages`.
You will also need to enable [32-bit GPU driver support](Installing-Graphics-Libraries).

### Arch / Manjaro / Endeavour or other Arch derivatives

##### Installation via AUR helper

You can install Grapejuice via an AUR helper, which is generally easier. AUR helpers aren't supported by Arch Linux though, so use at your own risk.
[Arch Wiki: AUR helpers](https://wiki.archlinux.org/title/AUR_helpers)

##### Installation via makepkg
`makepkg` is the manual and traditional way of installing an AUR package. It is the method supported by Arch Linux.
```sh
git clone --depth=1 https://aur.archlinux.org/grapejuice-git.git /tmp/grapejuice-git
cd /tmp/grapejuice-git
makepkg -si
```

### Debian / Ubuntu / Pop!_OS / Mint or other Debian derivatives

First, we'll need to enable 32-bit support as 32-bit libraries are still required by Roblox:
```sh
sudo dpkg --add-architecture i386
```

Install Grapejuice's keyring by running:
```sh
curl https://gitlab.com/brinkervii/grapejuice/-/raw/master/ci_scripts/signing_keys/public_key.gpg | sudo tee /usr/share/keyrings/grapejuice-archive-keyring.gpg
```

To get access to the Grapejuice package, you'll need to add the repository. Do that using:
```
sudo tee /etc/apt/sources.list.d/grapejuice.list <<< 'deb [signed-by=/usr/share/keyrings/grapejuice-archive-keyring.gpg] https://brinkervii.gitlab.io/grapejuice/repositories/debian/ universal main'
```

Since a new repository was added, you'll need to update your system so the package can be found:
```sh
sudo apt update && sudo apt upgrade -y
```

Now, it's time to install the Grapejuice package:
```sh
sudo apt install -y grapejuice
```

---

Once Grapejuice has been installed, you can proceed to the section below.

### Musl based distros

See the [flatpak guide](Installing-from-flatpak).

Alternatively, you can use a chroot for your system, see the appropriate guide for your distribution.

## 🍷 Installing Wine

**You will need to install Wine before you can use Grapejuice**.
See [this guide](Installing-Wine) for instructions on installing Wine.

## 🤔 Still having issues?

Even after installing Grapejuice and the patched wine version above, you may still have issues (examples: bad performance, Roblox not opening, etc). Usually, you can find the solutions here: [Troubleshooting page](Troubleshooting)
