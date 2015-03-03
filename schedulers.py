#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 13:42:34
# @Last Modified by:   caktux
# @Last Modified time: 2015-03-03 13:30:23

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.

from buildbot.schedulers.basic import AnyBranchScheduler, SingleBranchScheduler
from buildbot.schedulers.forcesched import *
from buildbot.schedulers.timed import Nightly
from buildbot.schedulers.triggerable import Triggerable
from buildbot.changes import filter

schedulers = []

self_codebases={
    'ethereum-buildbot': {
        'repository': 'https://github.com/ethereum/ethereum-buildbot.git',
        'branch': 'master',
        'revision': None
    }
}
dockers_codebases={
    'ethereum-dockers': {
        'repository': 'https://github.com/ethereum/ethereum-dockers.git',
        'branch': 'master',
        'revision': None
    }
}
cpp_ethereum_codebases={
    'cpp-ethereum': {
        'repository': 'https://github.com/ethereum/cpp-ethereum.git',
        'branch': None,
        'revision': None
    },
    'tests': {
        'repository': 'https://github.com/ethereum/tests.git',
        'branch': None,
        'revision': None
    }
}
go_ethereum_codebases={
    'go-ethereum': {
        'repository': 'https://github.com/ethereum/go-ethereum.git',
        'branch': None,
        'revision': None
    },
    'go-build': {
        'repository': 'https://github.com/ethereum/go-build.git',
        'branch': None,
        'revision': None
    }
}
ethereumj_codebases={
    'ethereumj': {
        'repository': 'https://github.com/ethereum/ethereumj.git',
        'branch': 'master',
        'revision': None
    }
}
pyethereum_codebases={
    'pyethereum': {
        'repository': 'https://github.com/ethereum/pyethereum.git',
        'branch': None,
        'revision': None
    }
}
serpent_codebases={
    'serpent': {
        'repository': 'https://github.com/ethereum/serpent.git',
        'branch': None,
        'revision': None
    }
}
brew_codebases={
    'homebrew-ethereum': {
        'repository': 'https://github.com/ethereum/homebrew-ethereum.git',
        'branch': 'master',
        'revision': None
    }
}
ethereumjs_codebases={
    'ethereumjs': {
        'repository': 'https://github.com/ethereum/ethereum.js.git',
        'branch': 'master',
        'revision': None
    }
}
integration_codebases={
    'integration': {
        'repository': 'https://github.com/etherex/etherex.git',
        'branch': 'master',
        'revision': None
    }
}

all_cpp_ethereum_codebases=cpp_ethereum_codebases.copy()
all_cpp_ethereum_codebases.update(brew_codebases)

all_go_ethereum_codebases=go_ethereum_codebases.copy()
all_go_ethereum_codebases.update(brew_codebases)

all_ethereumj_codebases=ethereumj_codebases.copy()

all_pyethereum_codebases=pyethereum_codebases.copy()

all_serpent_codebases=serpent_codebases.copy()

all_brew_cpp_codebases=cpp_ethereum_codebases.copy()
all_brew_cpp_codebases.update(brew_codebases)

all_brew_go_codebases=go_ethereum_codebases.copy()
all_brew_go_codebases.update(brew_codebases)

all_integration_codebases=cpp_ethereum_codebases.copy()
all_integration_codebases.update(ethereumjs_codebases)
all_integration_codebases.update(integration_codebases)


for scheduler in [
    SingleBranchScheduler(
        name="ethereum-buildbot-git",
        change_filter=filter.ChangeFilter(project='ethereum-buildbot', branch='master'),
        codebases=self_codebases,
        treeStableTimer=60,
        builderNames=["buildbot"]),
]: schedulers.append(scheduler)

for branch in ['master', 'develop']:
    for scheduler in [
        SingleBranchScheduler(
            name="cpp-ethereum-%s-git" % branch,
            change_filter=filter.ChangeFilter(project='cpp-ethereum', branch=branch),
            codebases=all_cpp_ethereum_codebases,
            treeStableTimer=60,
            builderNames=[
                "Linux C++ %s branch" % branch,
                "Linux C++ %s evmjit" % branch,
                "OSX C++ %s branch" % branch,
                "OSX C++ %s evmjit" % branch,
                "Windows C++ %s branch" % branch]),
        SingleBranchScheduler(
            name="go-ethereum-%s-git" % branch,
            change_filter=filter.ChangeFilter(project='go-ethereum', branch=branch),
            codebases=all_go_ethereum_codebases,
            treeStableTimer=60,
            builderNames=[
                "Linux Go %s branch" % branch,
                "OSX Go %s branch" % branch]),
        SingleBranchScheduler(
            name="pyethereum-%s-git" % branch,
            change_filter=filter.ChangeFilter(project='pyethereum', branch=branch),
            codebases=all_pyethereum_codebases,
            treeStableTimer=60,
            builderNames=[
                "Linux PyEthereum %s" % branch,
                "OSX PyEthereum %s" % branch]),
        SingleBranchScheduler(
            name="serpent-%s-git" % branch,
            change_filter=filter.ChangeFilter(project='serpent', branch=branch),
            codebases=all_serpent_codebases,
            treeStableTimer=60,
            builderNames=[
                "Linux Serpent %s" % branch,
                "OSX Serpent %s" % branch]),

        # Brew triggerables
        Triggerable(
            name="cpp-ethereum-%s-brew" % branch,
            builderNames=["OSX C++ %s brew" % branch],
            codebases=all_cpp_ethereum_codebases),
        Triggerable(
            name="go-ethereum-%s-brew" % branch,
            builderNames=["OSX Go %s brew" % branch],
            codebases=all_go_ethereum_codebases),

        # Extra triggerable checks
        Triggerable(
            name="cpp-ethereum-%s-check" % branch,
            builderNames=["Linux C++ %s check" % branch],
            codebases=all_cpp_ethereum_codebases),
        Triggerable(
            name="cpp-ethereum-%s-osx-check" % branch,
            builderNames=["OSX C++ %s check" % branch],
            codebases=all_cpp_ethereum_codebases),

        # PoC node servers
        Triggerable(
            name="cpp-ethereum-%s-server" % branch,
            builderNames=["Linux C++ %s server" % branch],
            codebases=all_cpp_ethereum_codebases)
    ]: schedulers.append(scheduler)

    for architecture in ['i386', 'amd64']:
        for distribution in ['trusty', 'utopic']:
            for scheduler in [
                Triggerable(
                    name="cpp-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    builderNames=["Linux C++ %s deb %s-%s" % (branch, architecture, distribution)]),
                Triggerable(
                    name="go-ethereum-%s-%s-%s" % (branch, architecture, distribution),
                    builderNames=["Linux Go %s deb %s-%s" % (branch, architecture, distribution)])
            ]: schedulers.append(scheduler)

for scheduler in [
    SingleBranchScheduler(
        name="ethereumj-git",
        change_filter=filter.ChangeFilter(project='ethereumj', branch='master'),
        codebases=all_ethereumj_codebases,
        treeStableTimer=300,
        builderNames=["Linux EthereumJ"]),

    # Brew
    # SingleBranchScheduler(
    #     name="brew-cpp-git",
    #     change_filter=filter.ChangeFilter(project='brew', branch='master'),
    #     codebases=all_brew_cpp_codebases,
    #     treeStableTimer=300,
    #     builderNames=["OSX C++ master brew", "OSX C++ develop brew"]),
    # SingleBranchScheduler(
    #     name="brew-go-git",
    #     change_filter=filter.ChangeFilter(project='brew', branch='master'),
    #     codebases=all_brew_go_codebases,
    #     treeStableTimer=300,
    #     builderNames=["OSX Go master brew", "OSX Go develop brew"]),

    # Pull requests
    AnyBranchScheduler(
        name="cpp-ethereum-develop-pr-git",
        change_filter=filter.ChangeFilter(project='cpp-ethereum', category='pull-request'),
        codebases=all_cpp_ethereum_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux C++ pull requests",
            "Linux C++ evmjit pull requests",
            "OSX C++ pull requests",
            "OSX C++ evmjit pull requests",
            "Windows C++ pull requests"
        ]),
    AnyBranchScheduler(
        name="go-ethereum-develop-pr-git",
        change_filter=filter.ChangeFilter(project='go-ethereum', category='pull-request'),
        codebases=all_go_ethereum_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux Go pull requests",
            "OSX Go pull requests"
        ]),
    AnyBranchScheduler(
        name="pyethereum-pr-git",
        change_filter=filter.ChangeFilter(project='pyethereum', category='pull-request'),
        codebases=all_pyethereum_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux PyEthereum PRs",
            "OSX PyEthereum PRs"
        ]),
    AnyBranchScheduler(
        name="serpent-pr-git",
        change_filter=filter.ChangeFilter(project='serpent', category='pull-request'),
        codebases=all_serpent_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux Serpent PRs",
            "OSX Serpent PRs"
        ]),
    AnyBranchScheduler(
        name="ethereumj-pr-git",
        change_filter=filter.ChangeFilter(project='ethereumj', category='pull-request'),
        codebases=all_ethereumj_codebases,
        treeStableTimer=300,
        builderNames=[
            "Linux EthereumJ PRs"
        ]),

    # Integration tests
    Triggerable(
        name="cpp-ethereum-integration",
        builderNames=["Linux C++ integration"],
        codebases=all_integration_codebases)

]: schedulers.append(scheduler)


#
# Forced schedulers
#
for scheduler in [
    ForceScheduler(
        name="force-self-update",
        builderNames=["buildbot"],
        codebases=["ethereum-buildbot"])
]: schedulers.append(scheduler)

for buildslave in ["one", "two", "three", "four"]:
    for scheduler in [
        ForceScheduler(
            name="force-buildslave-cpp-%s" % buildslave,
            builderNames=["buildslave-cpp-%s" % buildslave],
            codebases=["ethereum-dockers"]),
        ForceScheduler(
            name="force-buildslave-go-%s" % buildslave,
            builderNames=["buildslave-go-%s" % buildslave],
            codebases=["ethereum-dockers"])
    ]: schedulers.append(scheduler)
for buildslave in ["one", "two"]:
    for scheduler in [
        ForceScheduler(
            name="force-buildslave-python-%s" % buildslave,
            builderNames=["buildslave-python-%s" % buildslave],
            codebases=["ethereum-dockers"]),
        ForceScheduler(
            name="force-buildslave-java-%s" % buildslave,
            builderNames=["buildslave-java-%s" % buildslave],
            codebases=["ethereum-dockers"])
    ]: schedulers.append(scheduler)

for branch in ['master', 'develop']:
    for scheduler in [
        ForceScheduler(
            name="force-cpp-ethereum-%s" % branch,
            builderNames=["Linux C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-evmjit" % branch,
            builderNames=["Linux C++ %s evmjit" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s" % branch,
            builderNames=["Linux Go %s branch" % branch],
            codebases=["go-ethereum"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-osx" % branch,
            builderNames=["OSX C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-osx-evmjit" % branch,
            builderNames=["OSX C++ %s evmjit" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s-osx" % branch,
            builderNames=["OSX Go %s branch" % branch],
            codebases=["go-ethereum", "go-build"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-brew" % branch,
            builderNames=["OSX C++ %s brew" % branch],
            codebases=["homebrew-ethereum", "cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s-brew" % branch,
            builderNames=["OSX Go %s brew" % branch],
            codebases=["homebrew-ethereum", "go-ethereum"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-win" % branch,
            builderNames=["Windows C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-pyethereum-%s" % branch,
            builderNames=["Linux PyEthereum %s" % branch],
            codebases=["pyethereum"]),
        ForceScheduler(
            name="force-serpent-%s" % branch,
            builderNames=["Linux Serpent %s" % branch],
            codebases=["serpent"]),
        ForceScheduler(
            name="force-pyethereum-osx-%s" % branch,
            builderNames=["OSX PyEthereum %s" % branch],
            codebases=["pyethereum"]),
        ForceScheduler(
            name="force-serpent-osx-%s" % branch,
            builderNames=["OSX Serpent %s" % branch],
            codebases=["serpent"])
    ]: schedulers.append(scheduler)

for scheduler in [
    ForceScheduler(
        name="force-ethereumj",
        builderNames=["Linux EthereumJ"],
        codebases=["ethereumj"]),

    # Pull requests
    # Linux
    ForceScheduler(
        name="force-cpp-ethereum-pr",
        builderNames=["Linux C++ pull requests"],
        codebases=["cpp-ethereum", "tests"]),
    ForceScheduler(
        name="force-cpp-ethereum-evmjit-pr",
        builderNames=["Linux C++ evmjit pull requests"],
        codebases=["cpp-ethereum", "tests"]),
    ForceScheduler(
        name="force-go-ethereum-pr",
        builderNames=["Linux Go pull requests"],
        codebases=["go-ethereum"]),
    ForceScheduler(
        name="force-pyethereum-pr",
        builderNames=["Linux PyEthereum PRs"],
        codebases=["pyethereum"]),
    ForceScheduler(
        name="force-serpent-pr",
        builderNames=["Linux Serpent PRs"],
        codebases=["pyethereum"]),
    ForceScheduler(
        name="force-ethereumj-pr",
        builderNames=["Linux EthereumJ PRs"],
        codebases=["ethereumj"]),

    # OSX
    ForceScheduler(
        name="force-cpp-ethereum-osx-pr",
        builderNames=["OSX C++ pull requests"],
        codebases=["cpp-ethereum", "tests"]),
    ForceScheduler(
        name="force-cpp-ethereum-osx-evmjit-pr",
        builderNames=["OSX C++ evmjit pull requests"],
        codebases=["cpp-ethereum", "tests"]),
    ForceScheduler(
        name="force-go-ethereum-osx-pr",
        builderNames=["OSX Go pull requests"],
        codebases=["go-ethereum", "go-build"]),
    ForceScheduler(
        name="force-pyethereum-osx-pr",
        builderNames=["OSX PyEthereum PRs"],
        codebases=["pyethereum"]),
    ForceScheduler(
        name="force-serpent-osx-pr",
        builderNames=["OSX Serpent PRs"],
        codebases=["serpent"]),

    # Windows
    ForceScheduler(
        name="force-cpp-ethereum-win-pr",
        builderNames=["Windows C++ pull requests"],
        codebases=["cpp-ethereum", "tests"]),

    # Integration
    ForceScheduler(
        name="force-cpp-ethereum-integration",
        builderNames=["Linux C++ integration"],
        codebases=["cpp-ethereum", "ethereumjs", "integration"])
]: schedulers.append(scheduler)

for buildslave in ["one", "two", "three", "four"]:
    for scheduler in [
        Nightly(
            name="nightly-buildslave-cpp-%s" % buildslave,
            builderNames=["buildslave-cpp-%s" % buildslave],
            codebases=dockers_codebases,
            branch=None,
            hour=3,
            minute=0),
        Nightly(
            name="nightly-buildslave-go-%s" % buildslave,
            builderNames=["buildslave-go-%s" % buildslave],
            codebases=dockers_codebases,
            branch=None,
            hour=3,
            minute=0)
    ]: schedulers.append(scheduler)
for buildslave in ["one", "two"]:
    for scheduler in [
        Nightly(
            name="nightly-buildslave-python-%s" % buildslave,
            builderNames=["buildslave-python-%s" % buildslave],
            codebases=dockers_codebases,
            branch=None,
            hour=3,
            minute=30),
        Nightly(
            name="nightly-buildslave-java-%s" % buildslave,
            builderNames=["buildslave-java-%s" % buildslave],
            codebases=dockers_codebases,
            branch=None,
            hour=3,
            minute=30)
    ]: schedulers.append(scheduler)

# for architecture in ['i386', 'amd64']:
for distribution in ['trusty', 'utopic']:
    for scheduler in [
        # Triggerable(
        #     name="libcryptopp-%s-%s" % (architecture, distribution),
        #     builderNames=["libcryptopp %s-%s" % (architecture, distribution)]),
        # Triggerable(
        #     name="libjson-rpc-cpp-%s-%s" % (architecture, distribution),
        #     builderNames=["libjson-rpc-cpp %s-%s" % (architecture, distribution)]),
        ForceScheduler(
            name="force-libcryptopp-%s-%s" % ("amd64", distribution),
            builderNames=["libcryptopp %s-%s" % ("amd64", distribution)],
            # codebases=["cryptopp"],
            repository=FixedParameter(name="repository", default=""),
            project=FixedParameter(name="project", default=""),
            branch=FixedParameter(name="branch", default="master"),
            revision=
                StringParameter(
                    name="revision",
                    label="Revision:<br>",
                    default="81fd1114fa64ee680ad642063aa29c3f62a44cdd",
                    required=True,
                    size=40),
            properties=[
                StringParameter(
                    name="version",
                    label="Version:<br>",
                    default="5.6.2",
                    required=True,
                    size=20)
            ]),
        ForceScheduler(
            name="force-libjson-rpc-cpp-%s-%s" % ("amd64", distribution),
            builderNames=["libjson-rpc-cpp %s-%s" % ("amd64", distribution)],
            # codebases=["json-rpc-cpp"],
            repository=FixedParameter(name="repository", default=""),
            project=FixedParameter(name="project", default=""),
            branch=FixedParameter(name="branch", default="master"),
            revision=
                StringParameter(
                    name="revision",
                    label="Revision:<br>",
                    default="5dce039508d17ed1717eacf46be34d1a1eea1c87",
                    required=True,
                    size=40),
            properties=[
                StringParameter(
                    name="version",
                    label="Version:<br>",
                    default="0.4.2",
                    required=True,
                    size=10)
            ])
    ]: schedulers.append(scheduler)
