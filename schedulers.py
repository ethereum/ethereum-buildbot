#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.

from buildbot.schedulers.basic import AnyBranchScheduler, SingleBranchScheduler
from buildbot.schedulers.forcesched import *
from buildbot.schedulers.timed import Nightly
from buildbot.schedulers.triggerable import Triggerable
from buildbot.changes import filter

distributions = ['trusty', 'vivid']
schedulers = []

self_codebases = {
    'ethereum-buildbot': {
        'repository': 'https://github.com/ethereum/ethereum-buildbot.git',
        'branch': 'master',
        'revision': None
    }
}
dockers_codebases = {
    'ethereum-dockers': {
        'repository': 'https://github.com/ethereum/ethereum-dockers.git',
        'branch': 'master',
        'revision': None
    }
}
cpp_ethereum_codebases = {
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
go_ethereum_codebases = {
    'go-ethereum': {
        'repository': 'https://github.com/ethereum/go-ethereum.git',
        'branch': None,
        'revision': None
    }
}
ethereumj_codebases = {
    'ethereumj': {
        'repository': 'https://github.com/ethereum/ethereumj.git',
        'branch': 'master',
        'revision': None
    }
}
pyethereum_codebases = {
    'pyethereum': {
        'repository': 'https://github.com/ethereum/pyethereum.git',
        'branch': None,
        'revision': None
    }
}
pyethapp_codebases = {
    'pyethapp': {
        'repository': 'https://github.com/ethereum/pyethapp.git',
        'branch': None,
        'revision': None
    }
}
serpent_codebases = {
    'serpent': {
        'repository': 'https://github.com/ethereum/serpent.git',
        'branch': None,
        'revision': None
    }
}
brew_codebases = {
    'homebrew-ethereum': {
        'repository': 'https://github.com/ethereum/homebrew-ethereum.git',
        'branch': 'master',
        'revision': None
    }
}
ethereumjs_codebases = {
    'ethereumjs': {
        'repository': 'https://github.com/ethereum/ethereum.js.git',
        'branch': 'master',
        'revision': None
    }
}
integration_codebases = {
    'integration': {
        'repository': 'https://github.com/etherex/etherex.git',
        'branch': 'master',
        'revision': None
    }
}

all_cpp_ethereum_codebases = cpp_ethereum_codebases.copy()
all_cpp_ethereum_codebases.update(brew_codebases)

all_go_ethereum_codebases = go_ethereum_codebases.copy()
all_go_ethereum_codebases.update(brew_codebases)

all_ethereumj_codebases = ethereumj_codebases.copy()

all_pyethereum_codebases = pyethereum_codebases.copy()
all_pyethapp_codebases = pyethapp_codebases.copy()

all_serpent_codebases = serpent_codebases.copy()
all_serpent_codebases.update(pyethereum_codebases)

all_brew_cpp_codebases = cpp_ethereum_codebases.copy()
all_brew_cpp_codebases.update(brew_codebases)

all_brew_go_codebases = go_ethereum_codebases.copy()
all_brew_go_codebases.update(brew_codebases)

all_integration_codebases = cpp_ethereum_codebases.copy()
all_integration_codebases.update(ethereumjs_codebases)
all_integration_codebases.update(integration_codebases)

def other_branches(branch):
    if branch not in ('master', 'develop'):
        return True
    return False

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
                "Linux C++ GUI %s branch" % branch,
                "Linux C++ %s evmjit" % branch,
                "OSX C++ %s branch" % branch,
                "OSX C++ GUI %s branch" % branch,
                "OSX C++ %s evmjit" % branch,
                "Windows C++ %s branch" % branch]),
        SingleBranchScheduler(
            name="go-ethereum-%s-git" % branch,
            change_filter=filter.ChangeFilter(project='go-ethereum', branch=branch),
            codebases=all_go_ethereum_codebases,
            treeStableTimer=60,
            builderNames=[
                "Linux Go %s branch" % branch,
                "ARM Go %s branch" % branch,
                "OSX Go %s branch" % branch,
                "Windows Go %s branch" % branch
            ]),
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
            builderNames=[
                "OSX C++ %s brew" % branch,
                "OSX C++ GUI %s brew" % branch],
            codebases=all_cpp_ethereum_codebases),
        Triggerable(
            name="go-ethereum-%s-brew" % branch,
            builderNames=[
                "OSX Go %s brew" % branch
            ],
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
        for distribution in distributions:
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
        name="pyethapp-git",
        change_filter=filter.ChangeFilter(project='pyethapp', branch='master'),
        codebases=all_pyethapp_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux PyEthApp",
            "OSX PyEthApp"]),
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
        change_filter=filter.ChangeFilter(codebase='cpp-ethereum', category='pull'),
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
        change_filter=filter.ChangeFilter(codebase='go-ethereum', category='pull'),
        codebases=all_go_ethereum_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux Go pull requests",
            "ARM Go pull requests",
            "OSX Go pull requests",
            "Windows Go pull requests"
        ]),
    AnyBranchScheduler(
        name="pyethereum-pr-git",
        change_filter=filter.ChangeFilter(codebase='pyethereum', category='pull'),
        codebases=all_pyethereum_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux PyEthereum PRs",
            "OSX PyEthereum PRs"
        ]),
    AnyBranchScheduler(
        name="pyethapp-pr-git",
        change_filter=filter.ChangeFilter(codebase='pyethapp', category='pull'),
        codebases=all_pyethapp_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux PyEthApp PRs",
            "OSX PyEthApp PRs"
        ]),
    AnyBranchScheduler(
        name="serpent-pr-git",
        change_filter=filter.ChangeFilter(codebase='serpent', category='pull'),
        codebases=all_serpent_codebases,
        treeStableTimer=60,
        builderNames=[
            "Linux Serpent PRs",
            "OSX Serpent PRs"
        ]),
    AnyBranchScheduler(
        name="ethereumj-pr-git",
        change_filter=filter.ChangeFilter(codebase='ethereumj', category='pull'),
        codebases=all_ethereumj_codebases,
        treeStableTimer=300,
        builderNames=[
            "Linux EthereumJ PRs"
        ]),

    # Integration tests
    # Triggerable(
    #     name="cpp-ethereum-integration",
    #     builderNames=["Linux C++ integration"],
    #     codebases=all_integration_codebases)

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

for buildslave in ["one", "two", "three", "four", "five", "six"]:
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
        # Linux C++/Go
        ForceScheduler(
            name="force-cpp-ethereum-%s" % branch,
            builderNames=["Linux C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-gui-%s" % branch,
            builderNames=["Linux C++ GUI %s branch" % branch],
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
            name="force-go-ethereum-arm-%s" % branch,
            builderNames=["ARM Go %s branch" % branch],
            codebases=["go-ethereum"]),

        # OSX C++/Go
        ForceScheduler(
            name="force-cpp-ethereum-%s-osx" % branch,
            builderNames=["OSX C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-gui-%s-osx" % branch,
            builderNames=["OSX C++ GUI %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-osx-evmjit" % branch,
            builderNames=["OSX C++ %s evmjit" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s-osx" % branch,
            builderNames=["OSX Go %s branch" % branch],
            codebases=["go-ethereum"]),
        ForceScheduler(
            name="force-cpp-ethereum-%s-brew" % branch,
            builderNames=["OSX C++ %s brew" % branch],
            codebases=["homebrew-ethereum", "cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-cpp-ethereum-gui-%s-brew" % branch,
            builderNames=["OSX C++ GUI %s brew" % branch],
            codebases=["homebrew-ethereum", "cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s-brew" % branch,
            builderNames=["OSX Go %s brew" % branch],
            codebases=["homebrew-ethereum", "go-ethereum"]),

        # Windows C++/Go
        ForceScheduler(
            name="force-cpp-ethereum-%s-win" % branch,
            builderNames=["Windows C++ %s branch" % branch],
            codebases=["cpp-ethereum", "tests"]),
        ForceScheduler(
            name="force-go-ethereum-%s-win" % branch,
            builderNames=["Windows Go %s branch" % branch],
            codebases=["go-ethereum"]),

        # Other schedulers
        ForceScheduler(
            name="force-pyethereum-%s" % branch,
            builderNames=["Linux PyEthereum %s" % branch],
            codebases=["pyethereum"]),
        ForceScheduler(
            name="force-serpent-%s" % branch,
            builderNames=["Linux Serpent %s" % branch],
            codebases=["serpent", "pyethereum"]),
        ForceScheduler(
            name="force-pyethereum-osx-%s" % branch,
            builderNames=["OSX PyEthereum %s" % branch],
            codebases=["pyethereum"]),
        ForceScheduler(
            name="force-serpent-osx-%s" % branch,
            builderNames=["OSX Serpent %s" % branch],
            codebases=["serpent", "pyethereum"])
    ]: schedulers.append(scheduler)

for scheduler in [
    ForceScheduler(
        name="force-pyethapp",
        builderNames=["Linux PyEthApp"],
        codebases=["pyethapp"]),
    ForceScheduler(
        name="force-pyethapp-osx",
        builderNames=["OSX PyEthApp"],
        codebases=["pyethapp"]),
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
        name="force-go-ethereum-arm-pr",
        builderNames=["ARM Go pull requests"],
        codebases=["go-ethereum"]),
    ForceScheduler(
        name="force-pyethereum-pr",
        builderNames=["Linux PyEthereum PRs"],
        codebases=["pyethereum"]),
    ForceScheduler(
        name="force-pyethapp-pr",
        builderNames=["Linux PyEthApp PRs"],
        codebases=["pyethapp"]),
    ForceScheduler(
        name="force-serpent-pr",
        builderNames=["Linux Serpent PRs"],
        codebases=["serpent", "pyethereum"]),
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
        codebases=["go-ethereum"]),
    ForceScheduler(
        name="force-pyethereum-osx-pr",
        builderNames=["OSX PyEthereum PRs"],
        codebases=["pyethereum"]),
    ForceScheduler(
        name="force-pyethapp-osx-pr",
        builderNames=["OSX PyEthApp PRs"],
        codebases=["pyethapp"]),
    ForceScheduler(
        name="force-serpent-osx-pr",
        builderNames=["OSX Serpent PRs"],
        codebases=["serpent", "pyethereum"]),

    # Windows
    ForceScheduler(
        name="force-cpp-ethereum-win-pr",
        builderNames=["Windows C++ pull requests"],
        codebases=["cpp-ethereum", "tests"]),
    ForceScheduler(
        name="force-go-ethereum-win-pr",
        builderNames=["Windows Go pull requests"],
        codebases=["go-ethereum"]),

    # Integration
    # ForceScheduler(
    #     name="force-cpp-ethereum-integration",
    #     builderNames=["Linux C++ integration"],
    #     codebases=["cpp-ethereum", "ethereumjs", "integration"]),

    # deb tester
    ForceScheduler(
        name="force-cpp-ethereum-deb-tester",
        builderNames=["Linux C++ deb tester"],
        # codebases=["cpp-ethereum", "tests"],
        repository=FixedParameter(name="repository", default=""),
        project=FixedParameter(name="project", default=""),
        branch=StringParameter(name="branch", default="develop"),
        revision=StringParameter(
            name="revision",
            label="Revision:<br>",
            default="4cfc62e199d0ecab3e3c452389690c589c9785e0",
            required=True,
            size=40),
        properties=[
            StringParameter(
                name="version",
                label="Version:<br>",
                default="0.9.29",
                required=True,
                size=10)
        ]),
]: schedulers.append(scheduler)

for buildslave in ["one", "two", "three", "four", "five", "six"]:
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
for distribution in distributions:
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
            revision=StringParameter(
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
            revision=StringParameter(
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
            ]),
        ForceScheduler(
            name="force-qtwebengine-%s-%s" % ("amd64", distribution),
            builderNames=["qtwebengine %s-%s" % ("amd64", distribution)],
            repository=FixedParameter(name="repository", default=""),
            project=FixedParameter(name="project", default=""),
            branch=StringParameter(name="branch", default="5.4.1"),
            revision=StringParameter(
                name="revision",
                label="Revision:<br>",
                default="72ff0b7d9600db642e2d2e95c78c70454bbdb5e7",
                required=True,
                size=40),
            properties=[
                StringParameter(
                    name="version",
                    label="Version:<br>",
                    default="v5.4.1",
                    required=True,
                    size=10)
            ]),
        ForceScheduler(
            name="force-golang-%s-%s" % ("amd64", distribution),
            builderNames=["golang %s-%s" % ("amd64", distribution)],
            properties=[
                StringParameter(
                    name="version",
                    label="Version:<br>",
                    default="2:1.5-0ubuntu1",
                    required=True,
                    size=10)
            ]),
        ForceScheduler(
            name="force-cmake-%s-%s" % ("amd64", distribution),
            builderNames=["cmake %s-%s" % ("amd64", distribution)],
            properties=[
                StringParameter(
                    name="version",
                    label="Version:<br>",
                    default="3.2.2-2ubuntu3",
                    required=True,
                    size=10)
            ])
    ]: schedulers.append(scheduler)

    if distribution in ['trusty']:
        for scheduler in [
            ForceScheduler(
                name="force-qt5-%s" % distribution,
                builderNames=["qt5 %s" % distribution],
                properties=[
                    StringParameter(
                        name="version",
                        label="Version:<br>",
                        default="5.4.1",
                        required=True,
                        size=10)
                ])
        ]: schedulers.append(scheduler)
