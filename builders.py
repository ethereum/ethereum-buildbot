#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 13:42:45
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-23 17:23:32

from buildbot import locks

import factories
reload(factories)

from factories import self_update
from factories import buildslaves
from factories import cpp_ethereum
from factories import cpp_ethereum_osx
from factories import cpp_ethereum_windows
from factories import go_ethereum
from factories import go_ethereum_osx
from factories import go_ethereum_brew
from factories import ethereumj
from factories import pyethereum
from factories import serpent
from factories import dependencies
from factories import debian
from factories import poc_servers

reload(self_update)
reload(buildslaves)
reload(cpp_ethereum)
reload(cpp_ethereum_osx)
reload(cpp_ethereum_windows)
reload(go_ethereum)
reload(go_ethereum_osx)
reload(go_ethereum_brew)
reload(ethereumj)
reload(pyethereum)
reload(serpent)
reload(dependencies)
reload(debian)
reload(poc_servers)

from factories.self_update import *
from factories.buildslaves import *
from factories.cpp_ethereum import *
from factories.cpp_ethereum_osx import *
from factories.cpp_ethereum_brew import *
from factories.cpp_ethereum_windows import *
from factories.go_ethereum import *
from factories.go_ethereum_osx import *
from factories.go_ethereum_brew import *
from factories.ethereumj import *
from factories.pyethereum import *
from factories.serpent import *
from factories.debian import *
from factories.poc_servers import *


####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which slaves can execute them.  Note that any particular build will
# only take place on one slave.

builders = []

self_lock = locks.SlaveLock("self_update", maxCount = 1)
build_lock = locks.SlaveLock("slave_builds", maxCount = 2)
package_lock = locks.SlaveLock("slave_packaging", maxCount = 4)
go_lock = locks.SlaveLock("go_builds", maxCount = 1)
osx_lock = locks.SlaveLock("osx_builds", maxCount = 2)
brew_lock = locks.SlaveLock("brew_builds", maxCount = 1)
win_lock = locks.SlaveLock("win_builds", maxCount = 2)

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
for buildslave in ['one', 'two', 'three', 'four']:
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

for branch in ['master', 'develop']:
    for builder in [
        BuilderConfig(
            name="Linux C++ %s branch" % branch,
            builddir="build-cpp-ethereum-%s-docker" % branch,
            slavenames=[
                "slave-cpp-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-four%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-one%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-two%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=cpp_ethereum_factory(branch=branch, deb=True),
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
                "slave-cpp-four%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-one%s" % ("" if branch == 'master' else "-develop"),
                "slave-cpp-two%s" % ("" if branch == 'master' else "-develop")
            ],
            factory=cpp_ethereum_factory(branch=branch, deb=True, evmjit=True),
            locks=[build_lock.access('counting')]),
        BuilderConfig(
            name="Linux Go %s branch" % branch,
            builddir="build-go-ethereum-%s-docker" % branch,
            slavenames=[
                "slave-go-one%s" % ("" if branch == 'master' else "-develop"),
                "slave-go-two%s" % ("" if branch == 'master' else "-develop"),
                "slave-go-three%s" % ("" if branch == 'master' else "-develop"),
                "slave-go-four%s" % ("" if branch == 'master' else "-develop"
            )],
            factory=go_ethereum_factory(branch=branch, deb=True),
            locks=[go_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s branch" % branch,
            builddir="build-cpp-osx-%s" % branch,
            slavenames=["osx"],
            factory=osx_cpp_factory(branch=branch),
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
            slavenames=["osx"],
            factory=osx_go_factory(branch=branch),
            locks=[osx_lock.access('counting')]),
        BuilderConfig(
            name="OSX C++ %s brew" % branch,
            builddir="build-cpp-osx-%s-brew" % branch,
            slavenames=["osx"],
            factory=brew_cpp_factory(branch=branch),
            locks=[brew_lock.access('counting')]),
        BuilderConfig(
            name="OSX Go %s brew" % branch,
            builddir="build-go-ethereum-%s-brew" % branch,
            slavenames=["osx"],
            factory=brew_go_factory(branch=branch),
            locks=[brew_lock.access('counting')]),
        BuilderConfig(
            name="Windows C++ %s branch" % branch,
            builddir="build-cpp-ethereum-%s-win" % branch,
            slavenames=["winslave"],
            factory=win_cpp_factory(branch=branch),
            locks=[win_lock.access('counting')]),
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
                "slave-cpp-two",
                "slave-cpp-three",
                "slave-cpp-four"
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
        for distribution in ['trusty', 'utopic']:
            for builder in [
                BuilderConfig(
                    name="Linux C++ %s deb %s-%s" % (branch, architecture, distribution),
                    builddir="build-cpp-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    slavenames=["slave-cpp-one-deb", "slave-cpp-two-deb"],
                    factory=deb_factory(
                        name="ethereum",
                        repourl="https://github.com/ethereum/cpp-ethereum.git",
                        ppabranch="master",
                        branch=branch,
                        architecture=architecture,
                        distribution=distribution),
                    locks=[package_lock.access('counting')]),
                BuilderConfig(
                    name="Linux Go %s deb %s-%s" % (branch, architecture, distribution),
                    builddir="build-go-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    slavenames=["slave-go-one-deb", "slave-go-two-deb"],
                    factory=deb_factory(
                        name="go-ethereum",
                        repourl="https://github.com/ethereum/go-ethereum.git",
                        ppabranch="go-ethereum%s" % ("-develop" if branch=='develop' else ""),
                        branch=branch,
                        architecture=architecture,
                        distribution=distribution),
                    locks=[package_lock.access('counting')])
            ]: builders.append(builder)

# deps deb packaging
# for architecture in ['i386', 'amd64']:
for distribution in ['trusty', 'utopic']:
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
            locks=[package_lock.access('counting')]),
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
            locks=[package_lock.access('counting')])
    ]: builders.append(builder)

for builder in [
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
            "slave-cpp-one-pr",
            "slave-cpp-two-pr",
            "slave-cpp-three-pr",
            "slave-cpp-four-pr"
        ],
        factory=cpp_ethereum_factory(branch='develop'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux C++ evmjit pull requests",
        builddir="build-cpp-ethereum-evmjit-pr",
        slavenames=[
            "slave-cpp-one-pr",
            "slave-cpp-two-pr",
            "slave-cpp-three-pr",
            "slave-cpp-four-pr"
        ],
        factory=cpp_ethereum_factory(branch='develop', evmjit=True),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux Go pull requests",
        builddir="build-go-ethereum-pr",
        slavenames=[
            "slave-go-one-pr",
            "slave-go-two-pr",
            "slave-go-three-pr",
            "slave-go-four-pr"
        ],
        factory=go_ethereum_factory(branch='develop'),
        locks=[build_lock.access('counting')]),
    BuilderConfig(
        name="Linux PyEthereum PRs",
        builddir="build-pyethereum-pr",
        slavenames=["slave-python-one-pr", "slave-python-two-pr"],
        factory=pyethereum_factory(branch='develop'),
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
        slavenames=["osx"],
        factory=osx_cpp_factory(branch='develop', isPullRequest=True),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX C++ evmjit pull requests",
        builddir="build-cpp-ethereum-osx-evmjit-pr",
        slavenames=["osx"],
        factory=osx_cpp_factory(branch=branch, isPullRequest=True, evmjit=True),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX Go pull requests",
        builddir="build-go-ethereum-osx-pr",
        slavenames=["osx"],
        factory=osx_go_factory(branch='develop', isPullRequest=True),
        locks=[osx_lock.access('counting')]),
    BuilderConfig(
        name="OSX PyEthereum PRs",
        builddir="build-pyethereum-osx-pr",
        slavenames=["osx"],
        factory=pyethereum_factory(branch='develop'),
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
        locks=[win_lock.access('counting')])

]: builders.append(builder)
