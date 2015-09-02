#!/usr/bin/env python
# -*- coding: utf-8 -*-

from buildbot import locks

import factories
reload(factories)

from factories import self_update
from factories import buildslaves
from factories import cpp_ethereum
from factories import cpp_ethereum_osx
from factories import cpp_ethereum_brew
from factories import cpp_ethereum_windows
from factories import go_ethereum
from factories import go_ethereum_arm
from factories import go_ethereum_osx
from factories import go_ethereum_brew
from factories import go_ethereum_windows
from factories import ethereumj
from factories import pyethereum
from factories import pyethapp
from factories import serpent
from factories import debian
from factories import debian_backport
from factories import poc_servers
from factories import integration

reload(self_update)
reload(buildslaves)
reload(cpp_ethereum)
reload(cpp_ethereum_osx)
reload(cpp_ethereum_brew)
reload(cpp_ethereum_windows)
reload(go_ethereum)
reload(go_ethereum_arm)
reload(go_ethereum_osx)
reload(go_ethereum_brew)
reload(go_ethereum_windows)
reload(ethereumj)
reload(pyethereum)
reload(pyethapp)
reload(serpent)
reload(debian)
reload(debian_backport)
reload(poc_servers)
reload(integration)

from factories.self_update import *
from factories.buildslaves import *
from factories.cpp_ethereum import *
from factories.cpp_ethereum_osx import *
from factories.cpp_ethereum_brew import *
from factories.cpp_ethereum_windows import *
from factories.go_ethereum import *
from factories.go_ethereum_arm import *
from factories.go_ethereum_osx import *
from factories.go_ethereum_brew import *
from factories.go_ethereum_windows import *
from factories.ethereumj import *
from factories.pyethereum import *
from factories.pyethapp import *
from factories.serpent import *
from factories.debian import *
from factories.debian_backport import *
from factories.poc_servers import *
from factories.integration import *


# ###### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which slaves can execute them.  Note that any particular build will
# only take place on one slave.

distributions = ['trusty', 'vivid']
builders = []

self_lock = locks.SlaveLock("self_update", maxCount=1)
build_lock = locks.SlaveLock("slave_builds", maxCount=2)
# package_lock = locks.SlaveLock("slave_packaging",
#                                 maxCount=4,
#                                 maxCountForSlave = {
#                                     'slave-cpp-one-deb': 2,
#                                     'slave-cpp-two-deb': 2,
#                                     'slave-go-one-deb': 2,
#                                     'slave-go-two-deb': 2 })
go_lock = locks.SlaveLock("go_builds", maxCount=1)
arm_lock = locks.SlaveLock("arm_builds", maxCount=1)
osx_lock = locks.SlaveLock("osx_builds", maxCount=2)
brew_lock = locks.SlaveLock("brew_builds", maxCount=1)
win_lock = locks.SlaveLock("win_builds", maxCount=2)
win_lock_go = locks.SlaveLock("win_go_builds", maxCount=1)

# Latent slaves for builders
max_latents = 20
latentslaves = []
maxperslave = {}
for n in range(1, max_latents + 1):
    name = "latentslave%s" % n
    latentslaves.append(name)
    maxperslave[name] = 1  # One build per latent buildslave
latent_lock = locks.SlaveLock("latent_builds",
                              maxCount=max_latents,
                              maxCountForSlave=maxperslave)

#
# Builders
#
from buildbot.config import BuilderConfig

builders = []

# Self-update builder
for builder in [
    BuilderConfig(
        name="buildbot",
        builddir="build-self",
        slavenames=["selfslave"],
        factory=self_update_factory(),
        locks=[self_lock.access('exclusive')])
]: builders.append(builder)

# Buildslave builders
for buildslave in ['one', 'two', 'three', 'four', 'five', 'six']:
    for builder in [
        BuilderConfig(
            name="buildslave-cpp-%s" % buildslave,
            builddir="build-buildslave-cpp-%s" % buildslave,
            slavenames=["buildslave-%s" % buildslave],
            factory=buildslave_factory("cpp", "cpp-ethereum"),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="buildslave-go-%s" % buildslave,
            builddir="build-buildslave-go-%s" % buildslave,
            slavenames=["buildslave-%s" % buildslave],
            factory=buildslave_factory("go", "go-ethereum"),
            locks=[build_lock.access('counting')])
    ]: builders.append(builder)

for buildslave in ['one', 'two']:
    for builder in [
        BuilderConfig(
            name="buildslave-python-%s" % buildslave,
            builddir="build-buildslave-python-%s" % buildslave,
            slavenames=["buildslave-%s" % buildslave],
            factory=buildslave_factory("python", "pyethereum"),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="buildslave-java-%s" % buildslave,
            builddir="build-buildslave-java-%s" % buildslave,
            slavenames=["buildslave-%s" % buildslave],
            factory=buildslave_factory("java", "ethereumj"),
            locks=[build_lock.access('counting')])
    ]: builders.append(builder)

# Main builders
for branch in ['master', 'develop']:
    for builder in [
        BuilderConfig(
            name="Linux C++ %s branch" % branch,
            builddir="build-cpp-ethereum-%s-docker" % branch,
            slavenames=[
                "slave-cpp-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-four%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=cpp_ethereum_factory(branch=branch, deb=True),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux C++ GUI %s branch" % branch,
            builddir="build-cpp-ethereum-gui-%s" % branch,
            slavenames=[
                "slave-cpp-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-four%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=cpp_ethereum_factory(branch=branch, deb=True, headless=False),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux C++ %s server" % branch,
            builddir="build-cpp-ethereum-%s-server" % branch,
            slavenames=["poc-server-%s" % branch],
            factory=cpp_ethereum_server_factory(branch=branch),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux C++ %s evmjit" % branch,
            builddir="build-cpp-ethereum-%s-evmjit" % branch,
            slavenames=[
                "slave-cpp-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-four%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=cpp_ethereum_factory(branch=branch, deb=True, evmjit=True),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux Go %s branch" % branch,
            builddir="build-go-ethereum-%s-docker" % branch,
            slavenames=[
                "slave-go-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-go-four%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=go_ethereum_factory(branch=branch, deb=True),
            locks=[go_lock.access('counting')]),
        BuilderConfig(
            name="ARM Go %s branch" % branch,
            builddir="build-go-ethereum-%s-arm" % branch,
            slavenames=[
                "slave-go-three-arm",
                "slave-go-four-arm"
            ],
            factory=arm_go_factory(branch=branch),
            locks=[arm_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s branch" % branch,
            builddir="build-cpp-osx-%s" % branch,
            slavenames=["osx", "osx-two"],
            factory=osx_cpp_factory(branch=branch),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ GUI %s branch" % branch,
            builddir="build-cpp-gui-osx-%s" % branch,
            slavenames=["osx"],
            factory=osx_cpp_factory(branch=branch, headless=False),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s evmjit" % branch,
            builddir="build-cpp-osx-%s-evmjit" % branch,
            slavenames=["osx"],
            factory=osx_cpp_factory(branch=branch, evmjit=True),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX Go %s branch" % branch,
            builddir="build-go-osx-%s" % branch,
            slavenames=["osx", "osx-two"],
            factory=osx_go_factory(branch=branch),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s brew" % branch,
            builddir="build-cpp-osx-%s-brew" % branch,
            slavenames=["osx", "osx-two"],
            factory=brew_cpp_factory(branch=branch),
            locks=[brew_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ GUI %s brew" % branch,
            builddir="build-cpp-gui-osx-%s-brew" % branch,
            slavenames=["osx"],
            factory=brew_cpp_factory(branch=branch, headless=False),
            locks=[brew_lock.access('counting')]),
        BuilderConfig(
            name="OSX Go %s brew" % branch,
            builddir="build-go-ethereum-%s-brew" % branch,
            slavenames=["osx", "osx-two"],
            factory=brew_go_factory(branch=branch),
            locks=[brew_lock.access('counting')]),
        BuilderConfig(
            name="Windows C++ %s branch" % branch,
            builddir="build-cpp-ethereum-%s-win" % branch,
            slavenames=["winslave"],
            factory=win_cpp_factory(branch=branch),
            locks=[win_lock.access('counting')]),
        BuilderConfig(
            name="Windows Go %s branch" % branch,
            builddir="build-go-win-%s" % branch,
            slavenames=["winslave-go"],
            factory=windows_go_factory(branch=branch),
            locks=[win_lock_go.access('counting')]),
        BuilderConfig(
            name="Linux PyEthereum %s" % branch,
            builddir="build-pyethereum-%s" % branch,
            slavenames=["slave-python-one", "slave-python-two"],
            factory=pyethereum_factory(branch=branch),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux Serpent %s" % branch,
            builddir="build-serpent-%s" % branch,
            slavenames=["slave-python-one", "slave-python-two"],
            factory=serpent_factory(branch=branch),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="OSX PyEthereum %s" % branch,
            builddir="build-pyethereum-osx-%s" % branch,
            slavenames=["osx"],
            factory=pyethereum_factory(branch=branch),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX Serpent %s" % branch,
            builddir="build-serpent-osx-%s" % branch,
            slavenames=["osx"],
            factory=serpent_factory(branch=branch),
            locks=[osx_lock.access('counting')]),

        # Extra checks
        BuilderConfig(
            name="Linux C++ %s check" % branch,
            builddir="build-cpp-ethereum-%s-check" % branch,
            slavenames=[
                "slave-cpp-one",
                "slave-cpp-two"
            ],
            factory=cpp_check_factory(branch=branch),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s check" % branch,
            builddir="build-cpp-ethereum-%s-osx-check" % branch,
            slavenames=["osx"],
            factory=osx_cpp_check_factory(branch=branch),
            locks=[osx_lock.access('counting')])
    ]: builders.append(builder)

    # deb packaging
    for architecture in ['i386', 'amd64']:
        for distribution in distributions:
            for builder in [
                BuilderConfig(
                    name="Linux C++ %s deb %s-%s" % (branch, architecture, distribution),
                    builddir="build-cpp-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    slavenames=latentslaves,
                    factory=deb_factory(
                        name="cpp-ethereum",
                        repourl="https://github.com/ethereum/cpp-ethereum.git",
                        ppabranch=branch,
                        branch=branch,
                        architecture=architecture,
                        distribution=distribution),
                    locks=[latent_lock.access('counting')]),
                BuilderConfig(
                    name="Linux Go %s deb %s-%s" % (branch, architecture, distribution),
                    builddir="build-go-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    slavenames=latentslaves,
                    factory=deb_factory(
                        name="ethereum",
                        repourl="https://github.com/ethereum/go-ethereum.git",
                        ppabranch="go-ethereum%s" % ("-develop" if branch == 'develop' else ""),
                        branch=branch,
                        architecture=architecture,
                        distribution=distribution),
                    locks=[latent_lock.access('counting')])
            ]: builders.append(builder)

# deps deb packaging
# for architecture in ['i386', 'amd64']:
for distribution in distributions:
    for builder in [
        BuilderConfig(
            name="libcryptopp %s-%s" % ("amd64", distribution),
            builddir="build-libcryptopp-%s-%s" % ("amd64", distribution),
            slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
            factory=deb_factory(
                name="libcryptopp",
                repourl="https://github.com/mmoss/cryptopp.git",
                ppabranch="libcrypto++",
                branch="master",
                architecture="amd64",
                distribution=distribution),
            locks=[latent_lock.access('counting')]),
        BuilderConfig(
            name="libjson-rpc-cpp %s-%s" % ("amd64", distribution),
            builddir="build-libjson-rpc-cpp-%s-%s" % ("amd64", distribution),
            slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
            factory=deb_factory(
                name="libjson-rpc-cpp",
                repourl="https://github.com/cinemast/libjson-rpc-cpp.git",
                ppabranch="libjson-rpc-cpp",
                branch="master",
                architecture="amd64",
                distribution=distribution),
            locks=[latent_lock.access('counting')]),
        BuilderConfig(
            name="qtwebengine %s-%s" % ("amd64", distribution),
            builddir="build-qtwebengine-%s-%s" % ("amd64", distribution),
            slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
            factory=deb_factory(
                name="qtwebengine-opensource-src",
                repourl="https://github.com/qtproject/qtwebengine.git",
                ppabranch="qt5webengine",
                branch="5.4.1",
                architecture="amd64",
                distribution=distribution),
            locks=[latent_lock.access('counting')]),
        BuilderConfig(
            name="golang %s-%s" % ("amd64", distribution),
            builddir="build-golang-%s-%s" % ("amd64", distribution),
            slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
            factory=backport_factory(
                name="golang",
                setVersion=True,
                repo="ethereum",
                architecture="amd64",
                distribution=distribution,
                packages=["golang"]),
            locks=[latent_lock.access('counting')]),
        BuilderConfig(
            name="cmake %s-%s" % ("amd64", distribution),
            builddir="build-cmake-%s-%s" % ("amd64", distribution),
            slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
            factory=backport_factory(
                name="cmake",
                setVersion=True,
                repo="ethereum",
                architecture="amd64",
                distribution=distribution,
                packages=["cmake"]),
            locks=[latent_lock.access('counting')])
    ]: builders.append(builder)

    if distribution in ['trusty']:
        for builder in [
            BuilderConfig(
                name="qt5 %s" % distribution,
                builddir="build-qt-%s" % distribution,
                slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
                factory=backport_factory(
                    name="qt5",
                    repo="ethereum-qt",
                    architecture="amd64",
                    distribution=distribution,
                    packages=[
                        "harfbuzz",
                        "libinput",
                        "qtbase-opensource-src",
                        "qtxmlpatterns-opensource-src",
                        "qtdeclarative-opensource-src",
                        "qtscript-opensource-src",
                        "qtwebsockets-opensource-src",
                        "qtwebkit-opensource-src",
                        "qttools-opensource-src",
                        "qtquick1-opensource-src",
                        "qtquickcontrols-opensource-src",
                        "qtlocation-opensource-src"
                    ]),
                locks=[latent_lock.access('counting')])
        ]: builders.append(builder)

for builder in [
    BuilderConfig(
        name="Linux PyEthApp",
        builddir="build-pyethapp",
        slavenames=["slave-python-one", "slave-python-two"],
        factory=pyethapp_factory(branch='master'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="OSX PyEthApp",
        builddir="build-pyethapp-osx",
        slavenames=["osx"],
        factory=pyethapp_factory(branch='master'),
        locks=[osx_lock.access('counting')]),

    BuilderConfig(
        name="Linux EthereumJ",
        builddir="build-ethereumj-docker",
        slavenames=["slave-java-one", "slave-java-two"],
        factory=ethereumj_factory(),
        locks=[build_lock.access('counting')]),

    # Pull requests
    # Linux
    BuilderConfig(
        name="Linux C++ pull requests",
        builddir="build-cpp-ethereum-pr",
        slavenames=[
            "slave-cpp-five-pr",
            "slave-cpp-six-pr"
        ],
        factory=cpp_ethereum_factory(branch='develop', headless=False),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux C++ evmjit pull requests",
        builddir="build-cpp-ethereum-evmjit-pr",
        slavenames=[
            "slave-cpp-five-pr",
            "slave-cpp-six-pr"
        ],
        factory=cpp_ethereum_factory(branch='develop', evmjit=True, headless=False),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux Go pull requests",
        builddir="build-go-ethereum-pr",
        slavenames=[
            "slave-go-five-pr",
            "slave-go-six-pr"
        ],
        factory=go_ethereum_factory(branch='develop'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="ARM Go pull requests",
        builddir="build-go-ethereum-arm-pr",
        slavenames=[
            "slave-go-five-arm",
            "slave-go-six-arm"
        ],
        factory=arm_go_factory(branch='develop', isPullRequest=True),
        locks=[arm_lock.access('counting')]),
    BuilderConfig(
        name="Linux PyEthereum PRs",
        builddir="build-pyethereum-pr",
        slavenames=["slave-python-one-pr", "slave-python-two-pr"],
        factory=pyethereum_factory(branch='develop'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux PyEthApp PRs",
        builddir="build-pyethapp-pr",
        slavenames=["slave-python-one-pr", "slave-python-two-pr"],
        factory=pyethapp_factory(branch='master'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux Serpent PRs",
        builddir="build-serpent-pr",
        slavenames=["slave-python-one-pr", "slave-python-two-pr"],
        factory=serpent_factory(branch='develop'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux EthereumJ PRs",
        builddir="build-ethereumj-pr",
        slavenames=["slave-java-one-pr", "slave-java-two-pr"],
        factory=ethereumj_factory(branch='master'),
        locks=[build_lock.access('counting')]),

    # OSX
    BuilderConfig(
        name="OSX C++ pull requests",
        builddir="build-cpp-ethereum-osx-pr",
        slavenames=["osx", "osx-two"],
        factory=osx_cpp_factory(branch='develop', isPullRequest=True, headless=False),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX C++ evmjit pull requests",
        builddir="build-cpp-ethereum-osx-evmjit-pr",
        slavenames=["osx"],
        factory=osx_cpp_factory(branch=branch, isPullRequest=True, evmjit=True, headless=False),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX Go pull requests",
        builddir="build-go-ethereum-osx-pr",
        slavenames=["osx", "osx-two"],
        factory=osx_go_factory(branch='develop', isPullRequest=True),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX PyEthereum PRs",
        builddir="build-pyethereum-osx-pr",
        slavenames=["osx"],
        factory=pyethereum_factory(branch='develop'),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX PyEthApp PRs",
        builddir="build-pyethapp-osx-pr",
        slavenames=["osx"],
        factory=pyethapp_factory(branch='master'),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX Serpent PRs",
        builddir="build-serpent-osx-pr",
        slavenames=["osx"],
        factory=serpent_factory(branch='develop'),
        locks=[osx_lock.access('counting')]),

    # Windows
    BuilderConfig(
        name="Windows C++ pull requests",
        builddir="build-cpp-ethereum-win-pr",
        slavenames=["winslave"],
        factory=win_cpp_factory(branch='develop', isPullRequest=True),
        locks=[win_lock.access('counting')]),
    BuilderConfig(
        name="Windows Go pull requests",
        builddir="build-go-ethereum-win-pr",
        slavenames=["winslave-go"],
        factory=windows_go_factory(branch='develop', isPullRequest=True),
        locks=[win_lock_go.access('counting')]),

    # Integration
    # BuilderConfig(
    #     name="Linux C++ integration",
    #     builddir="build-cpp-ethereum-integration",
    #     slavenames=[
    #         "slave-cpp-five-integration"
    #     ],
    #     factory=integration_factory(),
    #     locks=[build_lock.access('counting')]),

    BuilderConfig(
        name="Linux C++ deb tester",
        builddir="build-cpp-ethereum-deb-tester",
        slavenames=latentslaves,
        factory=deb_factory(
            name="cpp-ethereum",
            repourl="https://github.com/ethereum/cpp-ethereum.git",
            ppabranch="libethereum-lite",
            branch="master",
            architecture="amd64",
            distribution="vivid",
            testdeb=True),
        locks=[latent_lock.access('counting')]),

]: builders.append(builder)
