# Ethereum Buildbot Configuration

This project contains the configuration for the Ethereum Buildbot http://build.ethdev.com/
Changes to this repository are automatically deployed once they are pushed to GitHub.

## Configuration / Development

To create a local installation of buildbot (for development purposes):

```
git clone https://github.com/ethereum/ethereum-buildbot.git
cd ethereum-buildbot
pip install -r requirements.txt
buildbot create-master .
```

For local development purposes it is suggested to check the configuration `buildbot checkconfig` before pushing.
