First, download and install the Grapejuice keyring by running the following command in a Terminal window:
```sh
curl https://gitlab.com/brinkervii/grapejuice/-/raw/master/ci_scripts/signing_keys/public_key.gpg | sudo tee /usr/share/keyrings/grapejuice-archive-keyring.gpg
```

Next, add the Grapejuice package repository by running the following command in a Terminal window:
```sh
sudo tee /etc/apt/sources.list.d/grapejuice.list <<< 'deb [signed-by=/usr/share/keyrings/grapejuice-archive-keyring.gpg] https://brinkervii.gitlab.io/grapejuice/repositories/debian/ universal main'
```

Before actually installing the package, make sure your system is up to date by running the following command in a Terminal window:
```sh
sudo apt update && sudo apt upgrade -y
```

Finally, install the Grapejuice package by running the following command in a Terminal window:
```sh
sudo apt install -y grapejuice
```