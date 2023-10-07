title: Troubleshooting
---
This page describes some of the most common issues with Grapejuice and how to solve them. **Make sure you're using the
latest version of Grapejuice!** Do you have an issue that is not described here? Please let us know!

**Table of Contents**

[TOC]

---

# Roblox issue

## The in-game cursor doesn't lock after holding right-click to move the camera
This is due to an outdated version of Wine. See [Installing Wine](Installing-Wine).

This is due to a Roblox update causing an incompatibility with Wayland's handling of mouse events via XWayland. Switching to X11 on your display manager fixes this issue. see [#253](https://gitlab.com/brinkervii/grapejuice/-/issues/253)

## Game crashing with "An unexpected error occurred and Roblox needs to quit." or "You have been kicked due to unexpected client behaviour."

This is due to an outdated version of Wine. See [this guide](Installing-Wine).

## 'A valid wine binary could not be found' or 'Wine Home path is invalid or doesn't exist' or Error 268

This means that you do not have Wine installed or that your version of Wine does not function correctly. See [Installing Wine](Installing-Wine). Otherwise make sure you have roblox installed.

## Cannot log into studio

It is possible to log into studio, but the level of how broken it is at the moment seems to be based on your system configuration and/or which
A/B testing cell you are in. The "new" Roblox Studio login uses a Microsoft Edge Webview, which is extremely unstable under Wine.

You can try these below to get the login working:

1. Make sure Roblox Studio is closed.
2. Open Grapejuice and navigate to the Studio prefix. Under "Wine Apps" click "Kill Wineserver"
3. Close Grapejuice
4. Install the prebuilt Wine build from [Installing Wine](Installing-Wine) or get another custom wine build that has the childwindow patch
5. Open Grapejuice and navigate to the Studio prefix.
6. Click 'Open Drive C' and make a directory where you are going to put some installation files.
7. Download both the `x86` and `x64` installers from the "Evergreen Standalone Installer" section on this page: [Webview2 - Microsoft Edge Developer](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)
8. Take the installers you downloaded in step 7 and move them into the directory you created in step 6.
9. In Grapejuice, on the Studio prefix page, click on "Wine Apps" and open the "Explorer" tool.
10. Navigate to "My Computer", then "(C:)" and then the directory you created in step 6.
11. Double click `MicrosoftEdgeWebView2RuntimeInstallerX86.exe` and wait for the installation to finish.
12. Double click `MicrosoftEdgeWebView2RuntimeInstallerX64.exe` and wait for the installation to finish.
13. Close the explorer Window
14. Open Roblox Studio either through the desktop shortcut or through the Grapejuice start page.
15. Wait for the Studio login to fail. This might take a while.
16. You should get a dialog that prompts you to log in through Studio or through the Website.
17. Click the button to log in through the website.
18. A new web page should open in your default browser that lets you authenticate, and opens a Studio Auth link.
19. A new "Roblox is Loading" dialog should appear as if a new instance of Roblox Studio is about to open
20. If everything went right, Studio should now redirect you to the Studio homepage.

Stuff that can go wrong with this approach:

- You might need to enable DXVK when going through step 14 through 20. Sometimes not having it enabled might result in an infinite load.
- Step 18 will sometimes not open your default browser. This only appears to happen on setups that use a window manager only setup. If you have a setup like that, you might not have your MIME/protocol associations setup according to the XDG standard. Because a window manager only setup is completely custom, you will have to fix this yourself.

## Studio graphical issues

Studio graphical issues come in two different forms:

1. Occasional flickering of the main viewport
2. Flickering of Studio widgets based on PluginGUI

**Flickering of the main viewport** happens when changing focus of PluginGUI widgets while using the DX11 Roblox renderer. There is no
solution to this problem yet. You can switch to the OpenGL renderer, but this will cause other graphical issues. The issue may be
exaggerated when using DXVK. In that case the viewport might flicker black.

**Studio widgets flicker** most likely because switching OpenGL render targets/surfaces doesn't work flawlessly in Wine. If you do not
want widgets to flicker you have to switch to a Roblox Renderer that is **not** OpenGL.

## An error occurred trying to launch the experience. Please try again later.

If you're using Firefox, go to about:config or your user.js and set `network.http.referer.XOriginPolicy` to `1`
and `network.http.sendRefererHeader` to `2`. If that doesn't help, Something is wrong with your `user.js` configuration - see [#343](https://gitlab.com/brinkervii/grapejuice/-/issues/343)

## '(ID = 17: Connection attempt failed.)'

This could either mean that your router or installed firewall is blocking the Roblox protocol (eg. Router firewall set to High, UFW is enabled), or that the Roblox servers are down.

## Roblox launcher with the Roblox logo shows up, however the game does not start or `BadValue` X Error

Open the Grapejuice app, select `Player` on the left panel, and then enable `Use Mesa OpenGL version override`.

## Your computer's graphics card is not compatible with Roblox's minimum system requirements

Roblox isn't detecting your GPU drivers. See [Installing Graphics Libraries](Installing-Graphics-Libraries).

## Roblox doesn't launch or results in a black/white screen

See [Installing Graphics Libraries](Installing-Graphics-Libraries)
Afterwards, kill your wineserver via 'Wine Apps' on your wineprefix. If that doesn't help:

For OpenGL users:
1. Open the FFlag editor (Edit FFlags button in your wineprefix tab)
2. Search for `FFlagGraphicsGLUseDefaultVAO` in the search bar
3. Enable the FFlag `FFlagGraphicsGLUseDefaultVAO` and save changes

For DXVK users:

This may be caused by wine-mono not being installed or a newer system wine-mono version not meant for the wine version you're using. To install wine-mono uninstall DXVK, and run roblox, a prompt should pop up asking you to install wine-mono. If not then download the appropriate files from [wine](https://dl.winehq.org/wine/wine-mono/) and run

This may be caused by Wine Mono not being installed correctly. To solve this, open Grapejuice, go to the Player prefix, disable "Use DXVK D3D implementation", and then open an experience on Roblox.

If a prompt appears about installing Wine Mono, press "Install".

If the prompt doesn't appear, go [here](https://wiki.winehq.org/Mono#Versions) to find which Wine Mono version you need. Afterwards, go to the [Wine Mono download page](https://dl.winehq.org/wine/wine-mono/), find the folder with the Wine Mono version that you need, download the file that ends with `.msi`, and then run:

```sh
WINEPREFIX=~/.local/share/grapejuice/prefixes/player/ wine path/to/wine-mono.msi
```
Now open Grapejuice and enable "Use DXVK D3D implementation".

## Stuck on background task "Extracting Fast Flags"

Grapejuice extracts FFlags from Studio, if it isn't working it cannot extract it. Make sure to have it installed beforehand.

## Roblox crashes with custom FFlags
Reset the fflags you had set back to their normal state and see if it's reproducible, otherwise open a new issue. [#317](https://gitlab.com/brinkervii/grapejuice/-/issues/317)


## Built-in screen recorder doesn't work

You should consider using [another screen recorder](https://obsproject.com/).

If you need to use the built-in screen recorder, follow the below steps:

1. Open Grapejuice.
2. Select the player's wineprefix.
3. Select "Wine Apps" and open Winetricks.
4. Select the default wineprefix.
5. Click "Install a Windows DLL or component".
6. Install `qasf` and `wmp11`.

## Voice chat doesn't work

To use voice chat, you need to use Pipewire with pipewire-pulse.

## Desktop application is being used

This is part of the [app beta](https://devforum.roblox.com/t/925069). If you'd like to opt-out, go to the Grapejuice UI,
go to the player wineprefix, and disable "Desktop App".

## Non-QWERTY multiple layouts input issue

see [#345](https://gitlab.com/brinkervii/grapejuice/-/issues/345) and [#355](https://gitlab.com/brinkervii/grapejuice/-/issues/355)

# Graphical/Performance issue

## Game is slow or laggy/not enough FPS

see [Installing Graphics Libraries](Installing-Graphics-Libraries) and [Performance-Tweaks](Performance-Tweaks)

## DXVK being used despite being disabled

This is due to a system package forcing Wine to use DXVK, for fedora: remove `wine-dxvk`

## Roblox has tons of bloom

Use a different renderer, such as DXVK with DX11.

# Roblox FPS unlocker issue

## Roblox FPS unlocker doesn't work or crashes

This is due to wine versions 7.3 and up not working with the unlocker, See [Installing Wine](Installing-Wine).


## Roblox FPS unlocker duplicates in the System Tray

Right click on the rbxfpsunlocker icon in the tray and press 'close'
Otherwise, kill your wineserver via 'Wine Apps' on your wineprefix.

# Grapejuice issue

## json.decoder.JSONDecodeError

This means that the grapejuice configuration (JSON) is broken/has decoding errors, please remove it and re-do whatever setting changes you have made previously (eg. patched wine).
```
rm -rv ~/.config/brinkervii/grapejuice/user_settings.json
```
You can try to fix it manually if you don't want to remove it.

## The server name or address could not be resolved

Start the `nscd` service from `glibc`.

## Missing shared object libffi.so.[number]

Your system's `libffi` package may have upgraded, and the version of the .so file has increased. Just reinstalling
Grapejuice to fix the issue will not work in this case. Pip caches packages locally so they don't have to be
re-downloaded/rebuilt with new installations of a package, but this causes invalid links to shared objects to be cached
as well.

1. Remove the pip package cache: `rm -r ~/.cache/pip`
2. Reinstall Grapejuice

## no module named grapejuice

Your Grapejuice installation is broken, Re-install it with the appropriate guide's for your distribution - preferably [from package](Installing-from-package) if possible.
or update your system if you had installed from package.

## s3.amazonaws.com Max retries exceeded with url

Networking issue, Wait a bit before installing or launching Roblox or restart your Router.

## Grapejuice doesn't launch on SteamOS

See [Installing-from-source](Installing-from-source)


# Known issues with no known workarounds

- Window decorations (bar on the top of windows) can disappear after entering and exiting fullscreen.
- Screenshot key in the player doesn't work, but the screenshot button does.
- Non-QWERTY keyboard layouts can cause problems with controls.
- Could not install wine-tkg with error 522, This is because of the wine-tkg installer script being blocked in your country. [#299](https://gitlab.com/brinkervii/grapejuice/-/issues/299)
- The warning "Unable to read VR Path Registry" usually appears. However, this doesn't seem to affect anything.
