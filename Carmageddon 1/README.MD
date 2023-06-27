# About

this folder contains files from Nglide v21, dosbox-ece and some useful scripts for running Carmageddon 1 and expansions on Linux with better configurations and performance improvements like running on Vulkan and avoiding throttling for running directly with Dxvk and Nglide at the same time.

## Usage

* Install with [Lutris](https://lutris.net/games/carmageddon-max-pack/)

Need to install wine

* Debian and derivatives:
~~~
sudo apt install wine
~~~
* Arch and derivatives:
~~~
sudo pacman -S wine-staging
~~~
* Fedora and derivatives:
~~~
sudo dnf install wine
~~~
* Suse and derivatives:
~~~
sudo zypper install wine
~~~

### Download the [zipfile](https://github.com/Bugaboo2000/Lutris-scripts/releases/download/Layer/NglideC1.zip) and extract from your game folder

Set executable permissions:
~~~
chmod +x 'fix.sh' nglide_config.sh carma.sh carmahost.sh carmaclient.sh splat.sh splatclient.sh splathost.sh
~~~

### Open the terminal in your game folder and Run *fix.sh*

~~~
./fix.sh
~~~

## Using with Steam 

Into your Steam, *right click on game*, *Properties*,*General* and paste these parameters on *Initializing Options*:
~~~
 WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,SDL,SDL_net,winmm=n,b" WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosbox.exe -conf dosboxCARMA.conf -conf dosboxCARMA_single.conf -noconsole -c %command%
~~~

## Using with native Dosbox
