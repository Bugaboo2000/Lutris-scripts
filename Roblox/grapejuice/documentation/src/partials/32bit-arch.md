Roblox still relies on some 32-bit libraries. In order to make those work, you will have to enable 32-bit support on your installation.

Start off by editing the file `/etc/pacman.conf` In that file you will find a repository called `multilib` that is commented out by default. Uncomment the repository by removing the pound signs at the start of the lines pertaining to the multilib repository. Do not uncomment `multilib-testing` as it might cause issues with your system.

When you are done editing the `/etc/pacman.conf` file, the multilib section should look like this:
```toml
# If you want to run 32 bit applications on your x86_64 system,
# enable the multilib repositories as required here.

#[multilib-testing]
#Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist
```