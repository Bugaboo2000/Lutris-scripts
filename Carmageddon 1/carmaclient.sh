#!/bin/bash
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA_client.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA_client.conf
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosbox.exe -conf dosboxCARMA.conf -conf dosboxCARMA_client.conf -noconsole -c exit 	