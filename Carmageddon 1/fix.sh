#!/bin/bash

links() {
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA_single.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARMA_single.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARSPLAT.conf
ln -s $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT_single.conf $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/dosboxCARSPLAT_single.conf
}

configs() {
sed -i 's/output=\(.*\)/output=opengl/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i "s/fullresolution=.*$/fullresolution=$(xrandr | grep '*' | awk '{print $1}')/" config_file $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/memsize=\(.*\)/memsize=512/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
mv -F DOSBOX/ $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/ 
}

splat() {

sed -i 's/output=\(.*\)/output=opengl/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf
sed -i "s/fullresolution=.*$/fullresolution=$(xrandr | grep '*' | awk '{print $1}')/" config_file $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf
sed -i 's/memsize=\(.*\)/memsize=512/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARSPLAT.conf


}

fssetup() {
wget https://github.com/Bugaboo2000/Lutris-scripts/releases/download/Layer/NglideC1.zip && unzip NglideC1.zip -d $HOME/.local/share/Steam/steamapps/common/Carmageddon1/
WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/282010/ WINEDLLOVERRIDES="3DfxSpl2,glide,glide2x,glide3x,winmm=n,b" wine $HOME/.local/share/Steam/steamapps/common/Carmageddon1/DOSBOX/nglide_config.exe
}

links
wait
configs
wait
splat
wait
fssetup