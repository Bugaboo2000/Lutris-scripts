#!/bin/bash
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="libogg-0,liboggvorbis-0,libvorbisfile-3,glide,glide2x,glide3x,msvcp90,msvcr90,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosbox.exe -conf dosboxCARMA.conf -conf dosboxCARMA_single.conf -noconsole -c 