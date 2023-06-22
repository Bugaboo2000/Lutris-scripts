#!/bin/bash


Setup () {

wget https://github.com/Bugaboo2000/Lutris-scripts/releases/download/Layer/dosbox-ece-x86_64.AppImage
unzip nglide21.zip -d $HOME/.local/share/Steam/steamapps/common/Carmageddon1/

}




Configs() {
sed -i 's/output=\(.*\)/output=opengl/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i "s/fullresolution=.*$/fullresolution=$(xrandr | grep '*' | awk '{print $1}')/" config_file $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/memsize=\(.*\)/memsize=512/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
sed -i 's/glide=\(.*\)/glide=true/' $HOME/.local/share/Steam/steamapps/common/Carmageddon1/dosboxCARMA.conf
}