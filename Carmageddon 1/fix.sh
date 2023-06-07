#!/bin/bash

ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA_single.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA_single.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARSPLAT.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT_single.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARSPLAT_single.conf
wget https://github.com/Bugaboo2000/Lutris-scripts/releases/download/Layer/nglide21.zip
unzip nglide21.zip -d $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,SDL,SDL_net,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/nglide_config.exe

