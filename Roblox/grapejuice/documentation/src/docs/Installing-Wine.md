title: Install Wine
---

**Table of Contents**

[TOC]

It is generally recommended to install the `wine-staging` and `wine` (32bit) package provided by your distribution, as it comes with libraries such as for Audio and Font rendering and X/Wayland libraries, it is needed to run Roblox.
Unless you compile Wine yourself; In that case, install the dependencies manually.

**NOTE:** This will not override the already existing Wine in your system. It will install it in a separate folder.

## About Wine issues

Using Wine 8.0 or above is required; Otherwise, you will encounter a error saying that the wine version is unsupported.

If you're still facing issues, see [Troubleshooting](Troubleshooting)

## Installing vanilla Wine

If your distribution provides a package for Wine, usually named `wine`, which provides Wine 8.0 or above,
install that from your package manager. Vanilla Wine is usually recommended for usage as of now.
There are distro-specific steps as shown below:

### Debian 10/11/Testing

See [WineHQ Wiki: Debian](https://wiki.winehq.org/Debian)

### Ubuntu/Pop!_OS/Mint 22.04/21.10/20.04

See [WineHQ Wiki: Ubuntu](https://wiki.winehq.org/Ubuntu)

### Fedora 35/36

See [WineHQ Wiki: Fedora](https://wiki.winehq.org/Fedora)

### OpenSUSE

See [WineHQ Wiki: SUSE](https://en.opensuse.org/Wine#Repositories)

### Arch / Manjaro and its derivatives

Enable the `multilib` repository: [Arch Wiki: Official Repositories: multilib](https://wiki.archlinux.org/title/official_repositories#multilib)<br />
Update your system and install Wine + its dependencies after enabling `multilib`:
```sh
sudo pacman -Syu wine gnutls lib32-gnutls libpulse lib32-libpulse
```

### Void Linux

Enable the multilib repository: `sudo xbps-install void-repo-multilib`
```sh
xbps-install -Su wine wine-32bit libpulseaudio-32bit freetype-32bit libgcc-32bit
```

### Gentoo

Enabling `multilib` support in Gentoo Linux during installation isn't trivial, as it's usually enabled using profiles while installing your system. If that isn't the case, you should change to a `multilib` enabled profile to continue with this guide. Refer to [Gentoo Wiki: Profile](https://wiki.gentoo.org/wiki/Profile_(Portage) "`Profile`") on the Gentoo Wiki to change your profile, as just using eselect to change your profile and updating your `@world` set can render your installation unusable.

Synchronize the package database:
```sh
emerge --sync
```

For audio, If you're using `pipewire` make sure to compile both the 64-bit variant and the 32-bit variant, this can be done by running:
```sh
ABI_X86="64 32" emerge --ask media-video/pipewire
```
and check if `pipewire-pulse` is running. Refer to [Gentoo Wiki: Pipewire](https://wiki.gentoo.org/wiki/PipeWire) for more information.

If you're using `pulseaudio` compile the 64-bit and the 32-bit variant:
```sh
ABI_X86="64 32" emerge --ask media-sound/pulseaudio
```

For networking, make sure to install `gnutls` and its x86_32 variant:
```sh
ABI_X86="64 32" emerge --ask net-libs/gnutls
```
The `ABI_X86` flag is used to build both the 64-bit variant and the 32-bit variant.
Another way, and better way is to use `package.use` instead of manually adding the `ABI_X86` flag every time you update your system, refer to [Gentoo Wiki: /etc/portage/package.use](https://wiki.gentoo.org/wiki//etc/portage/package.use) if you don't know how.

**For installation of wine itself, see [Gentoo Wiki: Wine](https://wiki.gentoo.org/wiki/Wine)**

---

Otherwise, use the [download page for Wine](https://wiki.winehq.org/Download), or refer to your distribution's guides.

## Installing graphics dependencies

Graphics dependencies are needed to render Roblox graphics. It can result in crashes or white/black screens.
See [Installing Graphics Libraries](Installing-Graphics-Libraries).
