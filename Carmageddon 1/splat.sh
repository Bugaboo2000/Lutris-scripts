#!/bin/bash
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,SDL,SDL_net,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosbox.exe -conf dosboxCARSPLAT.conf -conf dosboxCARSPLAT_single.conf -noconsole -c exit