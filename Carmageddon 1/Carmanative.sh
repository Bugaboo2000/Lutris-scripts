#!/bin/bash 

LD_LIBRARY_PATH=/usr/local/lib dosbox-x -conf glide.conf
cd ~/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/ && ./dosbox-ece-x86_64.AppImage -conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf -conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA_single.conf -noconsole -c