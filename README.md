# Ethereum Buildbot

This project contains the configuration for the [Ethereum Buildbot](https://build.ethdev.com/waterfall)

Changes to this repository are automatically deployed once they are pushed to GitHub. Please open a pull request unless you really know what you are doing.


## Configuration / Development

This is to create a local installation of buildbot for development purposes or to test changes to the buildbot's configurations. 

Start by cloning this repository locally and follow the steps below for your platform.

```
git clone https://github.com/ethereum/ethereum-buildbot.git
cd ethereum-buildbot
```

### Ubuntu

Install Docker using the [official documentation](https://docs.docker.com/installation/ubuntulinux/). Following the "Docker-maintained Package Installation" is recommended, as opposed to the "Ubuntu-maintained Package Installation".

Make sure you have `pip` installed, then install the requirements:
```
sudo apt-get install python-pip
sudo pip install -r requirements.txt
```

### OSX

Install Docker and boot2docker using Homebrew:
```
brew install docker boot2docker
```

Install requirements:
```
pip install -r requirements.txt
```

### Common installation steps

Generate a new sqlite database:
```
buildbot upgrade-master .
```

Copy every `.sample` file to their respective filename without the `.sample` extension. Edit each file with your desired credentials and configurations if you plan on running the buildbot in a production environment, otherwise you can keep the default not-so-secret `secret` password.

Verify that your installation should work with:
```
buildbot checkconfig
```

You should get `Config file is good!` from the last step. Run `buildbot checkconfig` after making changes, especially before pushing changes or making pull requests. This will catch syntax errors and will notify you if you missed something in your buildbot configurations.

You should now be able to start your buildmaster instance with:
```
buildbot start .
```

### Buildslaves configuration

This part can get quite complex, make sure you have your thinking cap well adjusted, grab a coffee and be ready for a lot of tinkering. You've been warned.

Remember installing Docker earlier on? This is where it comes into play.

Make sure Docker is running and well configured. On OSX, you need to run `boot2docker up` and follow the instructions about environment variables. On Ubuntu, make sure `docker info` mentions it is using AUFS (you'll see `Storage Driver: aufs`).

Create a test buildslave, we'll call it `testslave` and put it in a folder with the same name:
```
buildslave create-slave testslave localhost testslave secret
```

That test buildslave will be used to create the other buildslaves using Docker containers.

On OSX, you can use that same technique to create a native OSX buildslave, just give it a different name or use `osx` for the currently configured buildslave name. Be careful as this will affect your main system since it is not running in a container.

Open `builders.py` and look for the `# Buildslave builders` section. Add your `testslave` to the `slavenames` parameter of the builder of your choice, or all the buildslave builders.

Save your change and reconfigure your buildmaster with:
```
buildbot reconfig .
```

You can now start your buildslave with:
```
buildslave start testslave
```

It should attach itself to your buildmaster. Once you have at least one instance of our `testslave` running and attached, you should see the builder become available in the waterfall. Trigger a forced build and enjoy the first run fail on a missing `buildbot.tac`. This is where tinkering really gets taken to a whole new level.

You'll need to enter the failing container and set the appropriate values in the right `buildbot.tac` file at the right location.

First, note your host's IP under Docker using `ifconfig` to find Docker's network interface. You need this to tell the buildslave we're trying to create to connect to your host's buildmaster.

Click on the `stdio` link of the failing step, and note the second line that should look like:
```
in dir /home/your_username/ethereum-buildbot/testslave/build-buildslave-cpp-one/build
```

Move to that folder:
```
cd /home/your_username/ethereum-buildbot/testslave/build-buildslave-cpp-one/build
```

Copy the failing buildslave's `buildbot.tac.sample` to `buildbot.tac`:
```
cp cpp-ethereum-buildslave/buildbot.tac.sample cpp-ethereum-buildslave/buildbot.tac
```

Edit the `buildbot.tac` file with your favorite editor:
```
vim cpp-ethereum-buildslave/buildbot.tac
```

Set `buildmaster_host` to your previously noted host IP. Make sure `slavename` and `passwd` also correspond to the buildslave you're trying to create.

Rinse and repeat for every buildslave.


### Useful tricks

Enter a running container with:
```
docker exec -ti CONTAINER_NAME bash
```

### Contributing

Make sure you have a local installation of the Ethereum Buildbot to test your changes, since any modification can greatly affect many builders and processes, and even bring the whole buildmaster to a halt if changes are blindly pushed to the repository. Pull requests are always welcome and recommended for any modification.
