#!/bin/bash

install_debian() {
    sudo apt install -y gettext \
    git \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-dev \
    virtualenv \
    pkg-config \
    mesa-utils \
    libcairo2-dev \
    gtk-update-icon-cache \
    desktop-file-utils \
    xdg-utils \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    gnutls-bin:i386
}

install_arch() {
    sudo pacman -S git \
    python-pip \
    python-virtualenv \
    python-setuptools \
    cairo \
    gtk3 \
    gobject-introspection \
    desktop-file-utils \
    xdg-utils \
    xdg-user-dirs \
    gtk-update-icon-cache \
    shared-mime-info \
    mesa-utils
}

install_fedora() {
  sudo dnf install gettext \
  git \ 
  python3-devel \ 
  python3-pip \ 
  python3-virtualenv \
  cairo-devel \
  gobject-introspection-devel \
  cairo-gobject-devel \
  make \
  xdg-utils \
  glx-utils
}

install_gentoo() {
  sudo emerge --ask sys-devel/gettext \
  dev-vcs/git \
  dev-python/pip \
  dev-python/virtualenv \
  x11-libs/cairo \
  x11-libs/gtk+ \
  dev-libs/gobject-introspection \
  dev-util/desktop-file-utils \
  x11-misc/xdg-utils \
  x11-misc/xdg-user-dirs \
  dev-util/gtk-update-icon-cache \
  x11-misc/shared-mime-info \
  x11-apps/mesa-progs
}

install_opensuse() {
  sudo zypper install gettext-runtime \
  git \
  python3-devel \
  python3-pip \
  python3-virtualenv \
  cairo-devel \
  gobject-introspection-devel \
  make \
  xdg-utils \
  gtk3-devel \
  python3-gobject-Gdk
}

install_solus() {
  sudo eopkg it -c system.devel
  sudo eopkg install gettext \
  git \
  python3-devel \
  virtualenv \
  libcairo-devel \
  xdg-utils
}

install_freebsd() {
  sudo pkg install gettext \
  git \
  py39-pip \
  py39-virtualenv \
  cairo \
  gtk3 \
  gobject-introspection \
  desktop-file-utils \
  xdg-utils \
  xdg-user-dirs \
  gtk-update-icon-cache \
  shared-mime-info \
  python38
}

install_voidlinux() {
  sudo xbps-install -S gettext \
  python3 \
  python3-pip \
  python3-wheel \
  python3-virtualenv \
  python3-psutil \
  python3-setuptools \
  python3-cairo \
  python3-gobject \
  cairo-devel \
  desktop-file-utils \
  xdg-user-dirs \
  xdg-utils \
  gtk-update-icon-cache \
  shared-mime-info \
  pkg-config gobject-introspection
}

install_slackware() {
  sudo slackpkg install gettext \
  gettext-tools \
  python3 \
  python-pip \
  virtualenv \
  cairo \
  pycairo \
  gobject-introspection \
  make \
  xdg-utils \
  p7zip
}

if [ -x "$(command -v apt)" ]; then
  install_debian

elif [ -x "$(command -v pacman)" ]; then
  install_arch

elif [ -x "$(command -v dnf)" ]; then
  install_fedora

elif [ -x "$(command -v emerge)" ]; then
  install_gentoo

elif [ -x "$(command -v zypper)" ]; then
  install_opensuse

elif [ -x "$(command -v eopkg)" ]; then
  install_solus

elif [ -x "$(command -v pkg)" ]; then
  install_freebsd

elif [ -x "$(command -v xbps-install)" ]; then
  install_voidlinux
elif [ -x "$(command -v slackpkg)" ]; then
  install_slackware  

else
  echo "System Not Supported."
fi

