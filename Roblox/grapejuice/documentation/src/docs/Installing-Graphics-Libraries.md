title: Install Graphics Libraries
---
## About Graphics libraries

Playing Roblox may result in a black or white screen, an empty skybox upon loading up, a "graphics card not compatible" pop-up, or a crash.

To fix this, 32-bit graphics libraries are required for certain distributions.

## Installing Graphics libraries

### Debian / Ubuntu / Pop!_OS / Mint or other Debian derivatives

apt will pull the required graphics driver required by your system already.

### Arch / Manjaro / Endeavour or other Arch derivatives

:warning: Make sure to enable 32-bit support see: [multilib repository](https://wiki.archlinux.org/title/Official_repositories#multilib).


- NVIDIA: `sudo pacman -S --needed lib32-nvidia-utils vulkan-icd-loader lib32-vulkan-icd-loader`  
- AMD: `sudo pacman -S --needed lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader`
- Intel: `sudo pacman -S --needed lib32-mesa vulkan-intel lib32-vulkan-intel vulkan-icd-loader lib32-vulkan-icd-loader`

### Fedora

dnf will pull the required graphics driver required by your system already.

To install Vulkan support: `sudo dnf install vulkan-loader vulkan-loader.i686`

### OpenSUSE

NVIDIA: The closed source NVIDIA driver is not available by default.
For Vulkan support: `sudo zypper in libvulkan1 libvulkan1-32bit`

- AMD: `sudo zypper in kernel-firmware-amdgpu libdrm_amdgpu1 libdrm_amdgpu1-32bit libdrm_radeon1 libdrm_radeon1-32bit libvulkan_radeon libvulkan_radeon-32bit libvulkan1 libvulkan1-32bit`
- Intel: `sudo zypper in kernel-firmware-intel libdrm_intel1 libdrm_intel1-32bit libvulkan1 libvulkan1-32bit libvulkan_intel libvulkan_intel-32bit`

### NixOS

Set `hardware.opengl.driSupport32Bit = true;` in `configuration.nix` to get 32-bit GPU drivers.
The `grapejuice` package will draw in all other dependencies.

### Void Linux

:warning: Make sure to enable 32-bit support: `sudo xbps-install void-repo-multilib`.

- NVIDIA: `sudo xbps-install nvidia-libs-32bit vulkan-loader vulkan-loader-32bit`
- AMD: `sudo xbps-install mesa-dri mesa-dri-32bit vulkan-loader vulkan-loader-32bit`
- Intel: `sudo xbps-install mesa-dri mesa-dri-32bit mesa-vulkan-intel mesa-vulkan-intel-32bit  vulkan-loader vulkan-loader-32bit`
