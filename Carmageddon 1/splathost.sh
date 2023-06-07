#!/bin/bash

ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT_server.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA_server.conf
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="libogg-0,liboggvorbis-0,libvorbisfile-3,glide,glide2x,glide3x,msvcp90,msvcr90,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosbox.exe -conf dosboxCARSPLAT.conf -conf dosboxCARSPLAT_server.conf -noconsole -c exit