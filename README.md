# Ethereum Buildbot Configuration

This project contains the configuration for the Ethereum Buildbot http://build.ethdev.com/
Changes to this repository are automatically deployed once they are pushed to GitHub.

## Configuration / Development

To create a local installation of buildbot (for development purposes). You'll need python, pip and virtualenv installed, also `libffi` development headers to be able to install `bcrypt`, which is a dependency of `txgithub`:

e.g. on Ubuntu

```
sudo apt-get install python-pip python-virtualenv libffi-dev
```

Then you can download, install and check `ethereum-buildbot`:

```
git clone https://github.com/ethereum/ethereum-buildbot.git
cd ethereum-buildbot
virtualenv- venv
source venv/bin/activate
pip install -r requirements.txt
buildbot create-master .
./generate_conf_from_sample.py
buildbot checkconfig
```

You should get "Config file is good!" from the last step. Run `buildbot checkconfig` again after you changed something.
It is currently not possible to actually start a local buildbot.
