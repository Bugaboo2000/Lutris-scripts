#!/bin/bash

links() {
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf $GAMEDIR/DOSBOX/dosboxCARMA.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA_single.conf $GAMEIDR/DOSBOX/dosboxCARMA_single.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf $GAMEDIR/DOSBOX/dosboxCARSPLAT.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT_single.conf $GAMEDIR/DOSBOX/dosboxCARSPLAT_single.conf
}

configs() {
sed -i 's/output=\(.*\)/output=opengl/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i "s/fullresolution=.*$/fullresolution=$(xrandr | grep '*' | awk '{print $1}')/" config_file $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/memsize=\(.*\)/memsize=512/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
}

splat() {

sed -i 's/output=\(.*\)/output=opengl/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf
sed -i "s/fullresolution=.*$/fullresolution=$(xrandr | grep '*' | awk '{print $1}')/" config_file $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf
sed -i 's/memsize=\(.*\)/memsize=512/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf


}

fssetup() {
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,winmm=n,b" wine $GAMEDIR/DOSBOX/nglide_config.exe
}

links
wait
configs
wait
splat
wait
fssetup